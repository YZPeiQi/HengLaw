package com.lexai.controller;

import com.lexai.common.Result;
import com.lexai.dto.DocumentGenerateRequest;
import com.lexai.service.DocumentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/document")
@RequiredArgsConstructor
public class DocumentController {

    private final DocumentService documentService;

    @PostMapping("/generate")
    public Result<Map<String, Object>> generate(Authentication authentication,
                                                 @Valid @RequestBody DocumentGenerateRequest request) {
        try {
            Long userId = getUserIdFromAuth(authentication);
            Map<String, Object> result = documentService.generateDocument(userId, request);
            return Result.success(result);
        } catch (Exception e) {
            return Result.error("文书生成失败：" + e.getMessage());
        }
    }

    @GetMapping("/list")
    public Result<List<Map<String, Object>>> list(Authentication authentication) {
        try {
            Long userId = getUserIdFromAuth(authentication);
            List<Map<String, Object>> documents = documentService.getUserDocuments(userId);
            return Result.success(documents);
        } catch (Exception e) {
            return Result.error("获取文书列表失败：" + e.getMessage());
        }
    }

    private Long getUserIdFromAuth(Authentication authentication) {
        return 1L;
    }
}
