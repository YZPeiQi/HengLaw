package com.lexai.repository;

import com.lexai.entity.CaseLibrary;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface CaseLibraryRepository extends JpaRepository<CaseLibrary, Long> {
    Page<CaseLibrary> findByCaseType(String caseType, Pageable pageable);

    @Query(value = "SELECT * FROM case_library WHERE case_title LIKE CONCAT('%',:keyword,'%') OR case_summary LIKE CONCAT('%',:keyword,'%') OR key_points LIKE CONCAT('%',:keyword,'%')",
        countQuery = "SELECT COUNT(*) FROM case_library WHERE case_title LIKE CONCAT('%',:keyword,'%') OR case_summary LIKE CONCAT('%',:keyword,'%') OR key_points LIKE CONCAT('%',:keyword,'%')",
        nativeQuery = true)
    Page<CaseLibrary> searchByKeyword(@Param("keyword") String keyword, Pageable pageable);

    @Query(value = "SELECT * FROM case_library WHERE case_type = :caseType AND (case_title LIKE CONCAT('%',:keyword,'%') OR case_summary LIKE CONCAT('%',:keyword,'%') OR key_points LIKE CONCAT('%',:keyword,'%'))",
        countQuery = "SELECT COUNT(*) FROM case_library WHERE case_type = :caseType AND (case_title LIKE CONCAT('%',:keyword,'%') OR case_summary LIKE CONCAT('%',:keyword,'%') OR key_points LIKE CONCAT('%',:keyword,'%'))",
        nativeQuery = true)
    Page<CaseLibrary> searchByKeywordAndType(@Param("keyword") String keyword, @Param("caseType") String caseType, Pageable pageable);

    @Query(value = "SELECT * FROM case_library ORDER BY RAND()",
        countQuery = "SELECT COUNT(*) FROM case_library",
        nativeQuery = true)
    Page<CaseLibrary> findRandomCases(Pageable pageable);
}
