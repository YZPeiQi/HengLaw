package com.lexai.controller;

import com.lexai.common.Result;
import com.lexai.dto.CaseAddRequest;
import com.lexai.dto.CaseAnalysisRequest;
import com.lexai.dto.CaseSearchRequest;
import com.lexai.service.CaseService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/case")
@RequiredArgsConstructor
public class CaseController {

    private final CaseService caseService;

    @PostMapping("/analyze")
    public Result<Map<String, Object>> analyze(Authentication authentication,
                                                @Valid @RequestBody CaseAnalysisRequest request) {
        try {
            Long userId = getUserIdFromAuth(authentication);
            Map<String, Object> result = caseService.analyzeCase(userId, request);
            return Result.success(result);
        } catch (Exception e) {
            return Result.error("案件分析失败：" + e.getMessage());
        }
    }

    @GetMapping("/search")
    public Result<Map<String, Object>> search(CaseSearchRequest request) {
        try {
            Map<String, Object> cases = caseService.searchCases(
                    request.getKeyword(),
                    request.getCaseType(),
                    request.getPage(),
                    request.getSize()
            );
            return Result.success(cases);
        } catch (Exception e) {
            return Result.error("案例检索失败：" + e.getMessage());
        }
    }

    @PostMapping("/add")
    public Result<String> addCase(@Valid @RequestBody CaseAddRequest request) {
        try {
            caseService.addCaseLibrary(request);
            return Result.success("添加成功");
        } catch (Exception e) {
            return Result.error("添加案例失败：" + e.getMessage());
        }
    }

    private Long getUserIdFromAuth(Authentication authentication) {
        return 1L;
    }
}
