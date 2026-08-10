package com.lexai.controller;

import com.lexai.common.Result;
import com.lexai.dto.ContractReviewRequest;
import com.lexai.service.ContractService;
import com.lexai.util.FileTextExtractor;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/contract")
@RequiredArgsConstructor
public class ContractController {

    private final ContractService contractService;
    private final FileTextExtractor fileTextExtractor;

    @PostMapping("/upload")
    public Result<Map<String, Object>> upload(Authentication authentication,
                                              @RequestParam("file") MultipartFile file) {
        try {
            if (file.isEmpty()) {
                return Result.error("请选择要上传的文件");
            }
            String content = fileTextExtractor.extractText(file);
            Map<String, Object> result = new HashMap<>();
            result.put("fileName", file.getOriginalFilename());
            result.put("content", content);
            return Result.success(result);
        } catch (Exception e) {
            return Result.error("文件解析失败：" + e.getMessage());
        }
    }

    @PostMapping("/review")
    public Result<Map<String, Object>> review(Authentication authentication,
                                              @Valid @RequestBody ContractReviewRequest request) {
        try {
            Long userId = getUserIdFromAuth(authentication);
            Map<String, Object> result = contractService.reviewContract(userId, request);
            return Result.success(result);
        } catch (Exception e) {
            return Result.error("合同审查失败：" + e.getMessage());
        }
    }

    @GetMapping("/list")
    public Result<List<Map<String, Object>>> list(Authentication authentication) {
        try {
            Long userId = getUserIdFromAuth(authentication);
            List<Map<String, Object>> contracts = contractService.getUserContracts(userId);
            return Result.success(contracts);
        } catch (Exception e) {
            return Result.error("获取合同列表失败：" + e.getMessage());
        }
    }

    private Long getUserIdFromAuth(Authentication authentication) {
        return 1L;
    }
}
