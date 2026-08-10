package com.lexai.service;

import com.lexai.dto.CaseAddRequest;
import com.lexai.dto.CaseAnalysisRequest;
import com.lexai.entity.Case;
import com.lexai.entity.CaseLibrary;
import com.lexai.entity.User;
import com.lexai.repository.CaseLibraryRepository;
import com.lexai.repository.CaseRepository;
import com.lexai.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class CaseService {

    private final CaseRepository caseRepository;
    private final CaseLibraryRepository caseLibraryRepository;
    private final UserRepository userRepository;
    private final AiService aiService;

    public Map<String, Object> analyzeCase(Long userId, CaseAnalysisRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("用户不存在"));

        Map<String, Object> analysisResult = aiService.analyzeCase(
                request.getCaseName(),
                request.getCaseType(),
                request.getCaseDescription()
        );

        String riskLevel = "中";
        if (analysisResult.containsKey("risk_level")) {
            riskLevel = (String) analysisResult.get("risk_level");
        } else if (analysisResult.containsKey("风险等级评估")) {
            riskLevel = (String) analysisResult.get("风险等级评估");
        }

        Case legalCase = Case.builder()
                .user(user)
                .caseName(request.getCaseName())
                .caseType(request.getCaseType())
                .caseDescription(request.getCaseDescription())
                .analysisResult(analysisResult)
                .riskLevel(riskLevel)
                .build();

        caseRepository.save(legalCase);

        Map<String, Object> result = new HashMap<>();
        result.put("id", legalCase.getId());
        result.put("analysis", analysisResult);
        result.put("riskLevel", riskLevel);

        return result;
    }

    public Map<String, Object> searchCases(String keyword, String caseType, int page, int size) {
        int safePage = Math.max(page, 1);
        int safeSize = Math.max(size, 1);
        PageRequest pageRequest = PageRequest.of(safePage - 1, safeSize, Sort.by(Sort.Direction.DESC, "createdAt"));

        Page<CaseLibrary> casePage;

        boolean hasKeyword = keyword != null && !keyword.trim().isEmpty();
        boolean hasType = caseType != null && !caseType.trim().isEmpty();

        if (hasKeyword && hasType) {
            casePage = caseLibraryRepository.searchByKeywordAndType(keyword.trim(), caseType.trim(), pageRequest);
        } else if (hasKeyword) {
            casePage = caseLibraryRepository.searchByKeyword(keyword.trim(), pageRequest);
        } else if (hasType) {
            casePage = caseLibraryRepository.findByCaseType(caseType.trim(), pageRequest);
        } else {
            casePage = caseLibraryRepository.findAll(pageRequest);
        }

        Map<String, Object> result = new HashMap<>();
        result.put("items", casePage.getContent().stream().map(this::toMap).toList());
        result.put("total", casePage.getTotalElements());
        result.put("page", safePage);
        result.put("size", safeSize);
        return result;
    }

    public void addCaseLibrary(CaseAddRequest request) {
        CaseLibrary caseLibrary = CaseLibrary.builder()
                .caseTitle(request.getCaseTitle())
                .caseType(request.getCaseType())
                .caseDate(request.getCaseDate())
                .caseRegion(request.getCaseRegion())
                .court(request.getCourt())
                .citedLaws(request.getCitedLaws())
                .caseSummary(request.getCaseSummary())
                .judgmentResult(request.getJudgmentResult())
                .judgmentReason(request.getJudgmentReason())
                .keyPoints(request.getKeyPoints())
                .similarCases(request.getSimilarCases())
                .caseText(request.getCaseText())
                .build();
        caseLibraryRepository.save(caseLibrary);
    }

    private Map<String, Object> toMap(CaseLibrary caseLibrary) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", caseLibrary.getId());
        map.put("caseTitle", caseLibrary.getCaseTitle());
        map.put("caseType", caseLibrary.getCaseType());
        map.put("caseDate", caseLibrary.getCaseDate());
        map.put("caseRegion", caseLibrary.getCaseRegion());
        map.put("court", caseLibrary.getCourt());
        map.put("citedLaws", caseLibrary.getCitedLaws());
        map.put("caseSummary", caseLibrary.getCaseSummary());
        map.put("judgmentResult", caseLibrary.getJudgmentResult());
        map.put("judgmentReason", caseLibrary.getJudgmentReason());
        map.put("keyPoints", caseLibrary.getKeyPoints());
        map.put("similarCases", caseLibrary.getSimilarCases());
        map.put("caseText", caseLibrary.getCaseText());
        return map;
    }
}
