package com.lexai.service;

import com.lexai.dto.ConsultationRequest;
import com.lexai.dto.ConsultationResponse;
import com.lexai.entity.Consultation;
import com.lexai.entity.User;
import com.lexai.repository.ConsultationRepository;
import com.lexai.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ConsultationService {

    private final ConsultationRepository consultationRepository;
    private final UserRepository userRepository;
    private final AiService aiService;

    public ConsultationResponse consult(Long userId, ConsultationRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("用户不存在"));

        String answer = aiService.consultation(
            request.getQuestion(),
            request.getCategory(),
            request.getModel()
        );

        Consultation consultation = Consultation.builder()
                .user(user)
                .question(request.getQuestion())
                .answer(answer)
                .category(request.getCategory())
                .build();

        consultation = consultationRepository.save(consultation);

        return toResponse(consultation);
    }

    public List<ConsultationResponse> getHistory(Long userId) {
        return consultationRepository.findByUserIdOrderByCreatedAtDesc(userId)
                .stream()
                .map(this::toResponse)
                .collect(Collectors.toList());
    }

    private ConsultationResponse toResponse(Consultation consultation) {
        return new ConsultationResponse(
                consultation.getId(),
                consultation.getQuestion(),
                consultation.getAnswer(),
                consultation.getCategory(),
                consultation.getCreatedAt() != null ?
                        consultation.getCreatedAt().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")) : ""
        );
    }
}
