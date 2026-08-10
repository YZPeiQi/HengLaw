package com.lexai.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class ContractReviewRequest {
    private String contractName;
    @NotBlank(message = "合同类型不能为空")
    private String contractType;
    @NotBlank(message = "合同内容不能为空")
    private String content;
    private String reviewMode = "basic";
    private String fileName;
}
