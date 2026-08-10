package com.lexai.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class DocumentGenerateRequest {
    @NotBlank(message = "文书类型不能为空")
    private String docType;
    private String title;
    private String partyA;
    private String partyB;
    private String caseDescription;
    private String claim;
}
