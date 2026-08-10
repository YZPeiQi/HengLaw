package com.lexai.repository;

import com.lexai.entity.Consultation;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ConsultationRepository extends JpaRepository<Consultation, Long> {
    List<Consultation> findByUserIdOrderByCreatedAtDesc(Long userId);
    Page<Consultation> findByUserId(Long userId, Pageable pageable);
    List<Consultation> findByCategory(String category);
}
