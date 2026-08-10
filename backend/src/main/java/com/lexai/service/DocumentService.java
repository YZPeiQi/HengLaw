package com.lexai.service;

import com.lexai.dto.DocumentGenerateRequest;
import com.lexai.entity.Document;
import com.lexai.entity.User;
import com.lexai.repository.DocumentRepository;
import com.lexai.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class DocumentService {

    private final DocumentRepository documentRepository;
    private final UserRepository userRepository;
    private final AiService aiService;

    public Map<String, Object> generateDocument(Long userId, DocumentGenerateRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("用户不存在"));

        String content = aiService.generateDocument(
                request.getDocType(),
                request.getTitle(),
                request.getPartyA(),
                request.getPartyB(),
                request.getCaseDescription(),
                request.getClaim()
        );

        Document document = Document.builder()
                .user(user)
                .docType(request.getDocType())
                .title(request.getTitle())
                .content(content)
                .build();

        documentRepository.save(document);

        Map<String, Object> result = new HashMap<>();
        result.put("id", document.getId());
        result.put("content", content);

        return result;
    }

    public List<Map<String, Object>> getUserDocuments(Long userId) {
        return documentRepository.findByUserIdOrderByCreatedAtDesc(userId)
                .stream()
                .map(this::toMap)
                .toList();
    }

    private Map<String, Object> toMap(Document document) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", document.getId());
        map.put("docType", document.getDocType());
        map.put("title", document.getTitle());
        map.put("createdAt", document.getCreatedAt() != null ?
                document.getCreatedAt().toString() : "");
        return map;
    }
}
