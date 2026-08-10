package com.lexai.controller;

import com.lexai.common.Result;
import com.lexai.service.TemplateSearchService;
import lombok.RequiredArgsConstructor;
import org.springframework.core.io.UrlResource;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/template")
@RequiredArgsConstructor
public class TemplateSearchController {

    private final TemplateSearchService templateSearchService;

    @GetMapping("/search")
    public Result<List<Map<String, Object>>> search(@RequestParam("keyword") String keyword,
                                                    @RequestParam(value = "limit", required = false) Integer limit) {
        try {
            return Result.success(templateSearchService.search(keyword, limit));
        } catch (Exception e) {
            return Result.error("模板搜索失败：" + e.getMessage());
        }
    }

    @GetMapping("/stats")
    public Result<Map<String, Object>> stats() {
        try {
            return Result.success(templateSearchService.stats());
        } catch (Exception e) {
            return Result.error("获取模板索引信息失败：" + e.getMessage());
        }
    }

    @PostMapping("/reindex")
    public Result<Map<String, Object>> reindex() {
        try {
            return Result.success("模板索引重建完成", templateSearchService.rebuildIndex());
        } catch (Exception e) {
            return Result.error("重建模板索引失败：" + e.getMessage());
        }
    }

    @PostMapping("/prewarm")
    public Result<Map<String, Object>> prewarm(@RequestBody(required = false) Map<String, Object> body) {
        try {
            Object idsObj = body == null ? null : body.get("ids");
            List<String> ids = idsObj instanceof List<?> raw
                    ? raw.stream().map(String::valueOf).collect(Collectors.toList())
                    : List.of();

            Object limitObj = body == null ? null : body.get("limit");
            Integer limit = limitObj instanceof Number number ? number.intValue() : null;

            return Result.success("模板预热完成", templateSearchService.prewarmPdfPreviews(ids, limit));
        } catch (Exception e) {
            return Result.error("模板预热失败：" + e.getMessage());
        }
    }

    @GetMapping("/preview/{id}")
    public Result<Map<String, Object>> preview(@PathVariable("id") String id) {
        try {
            return Result.success(templateSearchService.preview(id));
        } catch (Exception e) {
            return Result.error("模板预览失败：" + e.getMessage());
        }
    }

    @GetMapping("/download/{id}")
    public ResponseEntity<UrlResource> download(@PathVariable("id") String id) {
        try {
            Path path = templateSearchService.resolveDownloadPath(id);
            UrlResource resource = new UrlResource(path.toUri());
            String filename = path.getFileName().toString();

            HttpHeaders headers = new HttpHeaders();
            headers.setContentDisposition(ContentDisposition.attachment()
                    .filename(filename, StandardCharsets.UTF_8)
                    .build());

            return ResponseEntity.ok()
                    .headers(headers)
                    .contentType(MediaType.APPLICATION_OCTET_STREAM)
                    .body(resource);
        } catch (Exception e) {
            return ResponseEntity.notFound().build();
        }
    }

    @GetMapping("/pdf/{id}")
    public ResponseEntity<?> pdfPreview(@PathVariable("id") String id) {
        try {
            Path path = templateSearchService.resolvePdfPreviewPath(id);
            UrlResource resource = new UrlResource(path.toUri());

            HttpHeaders headers = new HttpHeaders();
            headers.setContentDisposition(ContentDisposition.inline()
                    .filename(path.getFileName().toString(), StandardCharsets.UTF_8)
                    .build());

            return ResponseEntity.ok()
                    .headers(headers)
                    .contentType(MediaType.APPLICATION_PDF)
                    .body(resource);
        } catch (Exception e) {
            return ResponseEntity.status(500)
                    .contentType(MediaType.TEXT_PLAIN)
                    .body("PDF预览失败：" + e.getMessage());
        }
    }
}
