package com.lexai.repository;

import com.lexai.entity.Case;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CaseRepository extends JpaRepository<Case, Long> {
    List<Case> findByUserIdOrderByCreatedAtDesc(Long userId);
    List<Case> findByCaseType(String caseType);
}
