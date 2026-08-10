package com.lexai.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class CaseAddRequest {

    @NotBlank(message = "案件名称不能为空")
    @Size(max = 200, message = "案件名称不能超过200个字")
    private String caseTitle;

    @NotBlank(message = "案件类型不能为空")
    private String caseType;

    private java.time.LocalDate caseDate;

    @Size(max = 100, message = "案件发生地域不能超过100个字")
    private String caseRegion;

    @Size(max = 100, message = "法院名称不能超过100个字")
    private String court;

    private java.util.List<String> citedLaws;

    @NotBlank(message = "案例摘要不能为空")
    private String caseSummary;

    @NotBlank(message = "判决结果不能为空")
    @Size(max = 100, message = "判决结果不能超过100个字")
    private String judgmentResult;

    private String judgmentReason;

    @NotBlank(message = "案件关键要点不能为空")
    private String keyPoints;

    private java.util.Map<String, Object> similarCases;

    private String caseText;
}