package com.lexai.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "case_library")
public class CaseLibrary {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(length = 200)
    private String caseTitle;

    @Column(length = 50)
    private String caseType;

    @Column(name = "case_date")
    private java.time.LocalDate caseDate;

    @Column(length = 100)
    private String caseRegion;

    @Column(length = 100)
    private String court;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "cited_laws", columnDefinition = "JSON")
    private java.util.List<String> citedLaws;

    @Column(columnDefinition = "TEXT")
    private String caseSummary;

    @Column(length = 100)
    private String judgmentResult;

    @Column(columnDefinition = "TEXT")
    private String judgmentReason;

    @Column(columnDefinition = "TEXT")
    private String keyPoints;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "similar_cases", columnDefinition = "JSON")
    private Map<String, Object> similarCases;

    @Column(columnDefinition = "TEXT")
    private String caseText;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
}
