package com.lexai.dto;

import lombok.Data;

@Data
public class CaseSearchRequest {
    private String keyword;
    private String caseType;
    private int page = 1;
    private int size = 8;
}
