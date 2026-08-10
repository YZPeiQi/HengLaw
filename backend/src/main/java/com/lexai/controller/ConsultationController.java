package com.lexai.controller;

import com.lexai.common.Result;
import com.lexai.dto.ConsultationRequest;
import com.lexai.dto.ConsultationResponse;
import com.lexai.service.ConsultationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/consultation")
@RequiredArgsConstructor
public class ConsultationController {

    private final ConsultationService consultationService;

    @PostMapping("/ask")
    public Result<ConsultationResponse> ask(Authentication authentication,
                                              @Valid @RequestBody ConsultationRequest request) {
        try {
            Long userId = getUserIdFromAuth(authentication);
            ConsultationResponse response = consultationService.consult(userId, request);
            return Result.success(response);
        } catch (Exception e) {
            return Result.error("咨询失败：" + e.getMessage());
        }
    }

    @GetMapping("/history")
    public Result<List<ConsultationResponse>> history(Authentication authentication) {
        try {
            Long userId = getUserIdFromAuth(authentication);
            List<ConsultationResponse> history = consultationService.getHistory(userId);
            return Result.success(history);
        } catch (Exception e) {
            return Result.error("获取历史记录失败：" + e.getMessage());
        }
    }

    private Long getUserIdFromAuth(Authentication authentication) {
        String username = authentication.getName();
        return 1L;
    }
}
