package com.lexai.service;

import lombok.extern.slf4j.Slf4j;
import org.apache.tika.exception.TikaException;
import org.apache.tika.metadata.Metadata;
import org.apache.tika.parser.AutoDetectParser;
import org.apache.tika.parser.ParseContext;
import org.apache.tika.sax.BodyContentHandler;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.xml.sax.SAXException;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Base64;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Stream;

@Service
@Slf4j
public class TemplateSearchService {

    @Value("${template.search.root-dir:../合同协议模板}")
    private String rootDir;

    @Value("${template.search.max-results:200}")
    private int defaultMaxResults;

    @Value("${template.preview.soffice-path:soffice}")
    private String sofficePath;

    @Value("${template.preview.convert-timeout-seconds:45}")
    private long convertTimeoutSeconds;

    private final AtomicReference<List<Path>> fileIndex = new AtomicReference<>(List.of());
    private volatile LocalDateTime indexedAt;
    private static final int MAX_PREVIEW_LENGTH = 20000;

    public List<Map<String, Object>> search(String keyword, Integer limit) {
        ensureIndexed();

        String safeKeyword = keyword == null ? "" : keyword.trim();
        if (safeKeyword.isBlank()) {
            return List.of();
        }

        int safeLimit = resolveLimit(limit);
        String[] tokens = safeKeyword.toLowerCase(Locale.ROOT).split("\\s+");
        Path rootPath = Paths.get(rootDir).toAbsolutePath().normalize();

        return fileIndex.get().stream()
            .map(path -> toSearchRow(rootPath, path, tokens))
            .filter(row -> (Integer) row.get("hitScore") > 0)
                .sorted(Comparator
                .comparing((Map<String, Object> row) -> (Integer) row.get("hitScore")).reversed()
                        .thenComparing(row -> (String) row.get("relativePath")))
                .limit(safeLimit)
                .map(this::removeInternalFields)
                .toList();
    }

    public Map<String, Object> preview(String id) {
        ensureIndexed();

        Path file = resolvePathById(id);
        String fileName = file.getFileName().toString();
        String ext = getExtension(fileName);
        boolean previewable = isPreviewable(ext);

        String content;
        if (previewable) {
            content = extractPreviewContent(file, ext);
            if (content == null || content.isBlank()) {
                content = "该文件暂不支持在线预览，请点击下载查看。";
            }
        } else {
            content = "该文件格式暂不支持在线预览，请点击下载查看。";
        }

        return Map.of(
                "id", id,
                "fileName", fileName,
                "ext", ext,
                "previewable", previewable,
                "content", content
        );
    }

    public Path resolveDownloadPath(String id) {
        ensureIndexed();
        return resolvePathById(id);
    }

    public Path resolvePdfPreviewPath(String id) {
        ensureIndexed();

        Path source = resolvePathById(id);
        String ext = getExtension(source.getFileName().toString());

        if ("pdf".equals(ext)) {
            return source;
        }

        if (!isOfficeConvertible(ext)) {
            throw new RuntimeException("当前文件类型不支持PDF在线预览");
        }

        return convertOfficeToPdf(source, id, ext);
    }

    public Map<String, Object> stats() {
        ensureIndexed();
        return Map.of(
                "rootDir", rootDir,
                "fileCount", fileIndex.get().size(),
                "indexedAt", indexedAt != null ? indexedAt.toString() : ""
        );
    }

    public Map<String, Object> rebuildIndex() {
        buildIndex();
        return stats();
    }

    public Map<String, Object> prewarmPdfPreviews(List<String> ids, Integer limit) {
        ensureIndexed();

        if (ids == null || ids.isEmpty()) {
            return Map.of(
                    "total", 0,
                    "converted", 0,
                    "skipped", 0,
                    "failed", 0,
                    "errors", List.of()
            );
        }

        int safeLimit = Math.min(Math.max(limit == null ? 12 : limit, 1), 50);
        List<String> safeIds = ids.stream()
                .filter(id -> id != null && !id.isBlank())
                .distinct()
                .limit(safeLimit)
                .toList();

        int converted = 0;
        int skipped = 0;
        int failed = 0;
        List<Map<String, String>> errors = new ArrayList<>();

        for (String id : safeIds) {
            try {
                Path source = resolvePathById(id);
                String ext = getExtension(source.getFileName().toString());
                if (!isOfficeConvertible(ext)) {
                    skipped++;
                    continue;
                }

                resolvePdfPreviewPath(id);
                converted++;
            } catch (Exception e) {
                failed++;
                if (errors.size() < 5) {
                    errors.add(Map.of(
                            "id", id,
                            "message", e.getMessage() == null ? "预热失败" : e.getMessage()
                    ));
                }
            }
        }

        return Map.of(
                "total", safeIds.size(),
                "converted", converted,
                "skipped", skipped,
                "failed", failed,
                "errors", errors
        );
    }

    private void ensureIndexed() {
        if (fileIndex.get().isEmpty()) {
            buildIndex();
        }
    }

    private synchronized void buildIndex() {
        Path rootPath = Paths.get(rootDir).toAbsolutePath().normalize();
        if (!Files.exists(rootPath) || !Files.isDirectory(rootPath)) {
            log.warn("模板目录不存在或不是文件夹: {}", rootPath);
            fileIndex.set(List.of());
            indexedAt = LocalDateTime.now();
            return;
        }

        List<Path> files = new ArrayList<>();
        try (Stream<Path> stream = Files.walk(rootPath)) {
            stream.filter(Files::isRegularFile).forEach(files::add);
        } catch (IOException e) {
            log.error("构建模板索引失败", e);
            fileIndex.set(List.of());
            indexedAt = LocalDateTime.now();
            return;
        }

        files.sort(Comparator.comparing(Path::toString));
        fileIndex.set(files);
        indexedAt = LocalDateTime.now();
        log.info("模板索引构建完成，数量={}", files.size());
    }

    private int resolveLimit(Integer limit) {
        int value = (limit == null || limit <= 0) ? defaultMaxResults : limit;
        return Math.min(value, 100000);
    }

    private Map<String, Object> toSearchRow(Path rootPath, Path fullPath, String[] tokens) {
        Path relative = rootPath.relativize(fullPath);
        String relativePath = relative.toString().replace('\\', '/');
        String fileName = fullPath.getFileName().toString();
        String fileNameLower = fileName.toLowerCase(Locale.ROOT);
        String relativePathLower = relativePath.toLowerCase(Locale.ROOT);
        String id = Base64.getUrlEncoder().withoutPadding()
            .encodeToString(relativePath.getBytes(StandardCharsets.UTF_8));

        int hitScore = calculateHitScore(fileNameLower, relativePathLower, tokens);

        long size = 0L;
        try {
            size = Files.size(fullPath);
        } catch (IOException ignored) {
        }

        return Map.of(
            "id", id,
                "fileName", fileName,
                "relativePath", relativePath,
                "ext", getExtension(fileName),
                "size", size,
            "previewable", isPreviewable(getExtension(fileName)),
            "hitScore", hitScore
        );
    }

    private int calculateHitScore(String fileName, String relativePath, String[] tokens) {
        int score = 0;
        for (String token : tokens) {
            if (token.isBlank()) {
                continue;
            }

            boolean inName = fileName.contains(token);
            boolean inPath = relativePath.contains(token);

            if (!inName && !inPath) {
                return 0;
            }

            if (inName) {
                score += 2;
            }
            if (inPath) {
                score += 1;
            }
        }
        return score;
    }

    private Map<String, Object> removeInternalFields(Map<String, Object> row) {
        return Map.of(
                "id", row.get("id"),
                "fileName", row.get("fileName"),
                "relativePath", row.get("relativePath"),
                "ext", row.get("ext"),
                "size", row.get("size"),
                "previewable", row.get("previewable")
        );
    }

    private Path resolvePathById(String id) {
        if (id == null || id.isBlank()) {
            throw new RuntimeException("模板ID不能为空");
        }

        String relativePath;
        try {
            relativePath = new String(Base64.getUrlDecoder().decode(id), StandardCharsets.UTF_8);
        } catch (Exception e) {
            throw new RuntimeException("模板ID非法");
        }

        Path rootPath = Paths.get(rootDir).toAbsolutePath().normalize();
        Path resolved = rootPath.resolve(relativePath).normalize();
        if (!resolved.startsWith(rootPath)) {
            throw new RuntimeException("无效模板路径");
        }
        if (!Files.exists(resolved) || !Files.isRegularFile(resolved)) {
            throw new RuntimeException("模板不存在");
        }
        return resolved;
    }

    private boolean isPreviewable(String ext) {
        if (ext == null || ext.isBlank()) {
            return false;
        }
        return switch (ext) {
            case "txt", "md", "csv", "json", "xml", "html", "htm", "js", "ts", "css", "java", "yml", "yaml", "properties", "sql", "doc", "docx", "wps", "pdf" -> true;
            default -> false;
        };
    }

    private boolean isOfficeConvertible(String ext) {
        return "doc".equals(ext) || "docx".equals(ext) || "wps".equals(ext);
    }

    private Path convertOfficeToPdf(Path source, String id, String ext) {
        try {
            Path workDir = Paths.get(System.getProperty("java.io.tmpdir"), "lexai-template-preview");
            Files.createDirectories(workDir);

            long lastModified = Files.getLastModifiedTime(source).toMillis();
            String token = Integer.toHexString((id + ":" + lastModified).hashCode());

            Path cachedPdf = workDir.resolve(token + ".pdf");
            if (Files.exists(cachedPdf) && Files.size(cachedPdf) > 0) {
                return cachedPdf;
            }

            Path tempInput = workDir.resolve(token + "." + ext);
            Files.copy(source, tempInput, StandardCopyOption.REPLACE_EXISTING);

            ProcessBuilder pb = new ProcessBuilder(
                    sofficePath,
                    "--headless",
                    "--nologo",
                    "--nolockcheck",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    workDir.toString(),
                    tempInput.toString()
            );
            pb.redirectErrorStream(true);

            Process process = pb.start();
            String output;
            try (InputStream in = process.getInputStream()) {
                output = new String(in.readAllBytes(), StandardCharsets.UTF_8);
            }

            boolean finished = process.waitFor(convertTimeoutSeconds, java.util.concurrent.TimeUnit.SECONDS);
            if (!finished) {
                process.destroyForcibly();
                throw new RuntimeException("PDF转换超时，请稍后重试");
            }

            if (process.exitValue() != 0) {
                throw new RuntimeException("PDF转换失败，可能未安装LibreOffice: " + output);
            }

            Path generatedPdf = workDir.resolve(token + ".pdf");
            if (!Files.exists(generatedPdf) || Files.size(generatedPdf) == 0) {
                throw new RuntimeException("PDF转换失败，未生成预览文件");
            }

            Files.deleteIfExists(tempInput);
            return generatedPdf;
        } catch (IOException e) {
            throw new RuntimeException("PDF转换失败，可能未安装LibreOffice或soffice不可用", e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("PDF转换被中断", e);
        }
    }

    private String extractPreviewContent(Path file, String ext) {
        try {
            String raw;
            if (isPlainTextExt(ext)) {
                raw = Files.readString(file, StandardCharsets.UTF_8);
            } else {
                raw = extractTextWithTika(file);
            }
            return normalizePreviewText(raw);
        } catch (Exception e) {
            log.warn("模板预览抽取失败: {}", file, e);
            return "";
        }
    }

    private boolean isPlainTextExt(String ext) {
        return switch (ext) {
            case "txt", "md", "csv", "json", "xml", "html", "htm", "js", "ts", "css", "java", "yml", "yaml", "properties", "sql" -> true;
            default -> false;
        };
    }

    private String extractTextWithTika(Path file) throws IOException, TikaException, SAXException {
        AutoDetectParser parser = new AutoDetectParser();
        Metadata metadata = new Metadata();
        BodyContentHandler handler = new BodyContentHandler(MAX_PREVIEW_LENGTH * 3);
        ParseContext context = new ParseContext();

        byte[] bytes = Files.readAllBytes(file);
        try (ByteArrayInputStream in = new ByteArrayInputStream(bytes)) {
            parser.parse(in, handler, metadata, context);
        }
        return handler.toString();
    }

    private String normalizePreviewText(String raw) {
        if (raw == null) {
            return "";
        }
        String cleaned = raw.replaceAll("[ \\t]+(?=\\r?\\n)", "");
        cleaned = cleaned.replaceAll("(\\r?\\n){3,}", "\n\n");
        cleaned = cleaned.trim();

        if (cleaned.length() > MAX_PREVIEW_LENGTH) {
            return cleaned.substring(0, MAX_PREVIEW_LENGTH) + "\n\n[内容较长，已截断显示，请下载查看完整内容]";
        }
        return cleaned;
    }

    private String getExtension(String fileName) {
        int idx = fileName.lastIndexOf('.');
        if (idx < 0 || idx == fileName.length() - 1) {
            return "";
        }
        return fileName.substring(idx + 1).toLowerCase(Locale.ROOT);
    }
}
