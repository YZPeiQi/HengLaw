package com.lexai.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class CaseAnalysisRequest {
    @NotBlank(message = "案件名称不能为空")
    private String caseName;
    @NotBlank(message = "案件类型不能为空")
    private String caseType;
    @NotBlank(message = "案件描述不能为空")
    private String caseDescription;
}
