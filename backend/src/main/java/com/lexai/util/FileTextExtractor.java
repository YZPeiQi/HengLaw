package com.lexai.util;

import lombok.extern.slf4j.Slf4j;
import org.apache.tika.Tika;
import org.apache.tika.exception.TikaException;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.UUID;

@Component
@Slf4j
public class FileTextExtractor {

    private final Tika tika = new Tika();

    public String extractText(MultipartFile file) throws IOException {
        String filename = file.getOriginalFilename();
        if (filename == null) {
            throw new IOException("文件名为空");
        }

        String lowerName = filename.toLowerCase();
        if (lowerName.endsWith(".pdf") || lowerName.endsWith(".docx") || lowerName.endsWith(".doc")) {
            return extractUsingTika(file.getInputStream());
        } else {
            throw new IOException("不支持的文件格式，请上传 .pdf、.docx 或 .doc 文件");
        }
    }

    public String extractFromPath(Path filePath) throws IOException {
        String filename = filePath.getFileName().toString().toLowerCase();
        if (filename.endsWith(".pdf") || filename.endsWith(".docx") || filename.endsWith(".doc")) {
            try (InputStream stream = Files.newInputStream(filePath)) {
                return extractUsingTika(stream);
            }
        } else {
            throw new IOException("不支持的文件格式");
        }
    }

    private String extractUsingTika(InputStream stream) throws IOException {
        try {
            String text = tika.parseToString(stream);
            return text;
        } catch (TikaException e) {
            log.error("Tika解析文件失败", e);
            throw new IOException("文件解析失败：" + e.getMessage());
        }
    }

    public String saveToTempFile(MultipartFile file) throws IOException {
        Path tempDir = Path.of(System.getProperty("java.io.tmpdir"));
        String suffix = getSuffix(file.getOriginalFilename());
        Path tempFile = tempDir.resolve(UUID.randomUUID() + suffix);
        Files.copy(file.getInputStream(), tempFile, StandardCopyOption.REPLACE_EXISTING);
        return tempFile.toString();
    }

    private String getSuffix(String filename) {
        if (filename == null) return "";
        int lastDot = filename.lastIndexOf('.');
        return lastDot > 0 ? filename.substring(lastDot) : "";
    }
}
