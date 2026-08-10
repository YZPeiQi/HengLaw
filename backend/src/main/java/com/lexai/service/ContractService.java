package com.lexai.service;

import com.lexai.dto.ContractReviewRequest;
import com.lexai.entity.Contract;
import com.lexai.entity.User;
import com.lexai.repository.ContractRepository;
import com.lexai.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class ContractService {

    private final ContractRepository contractRepository;
    private final UserRepository userRepository;
    private final AiService aiService;

    public Map<String, Object> reviewContract(Long userId, ContractReviewRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("用户不存在"));

        // 如果 contractName 为空，使用 fileName 作为合同名
        String contractName = request.getContractName();
        if (contractName == null || contractName.isBlank()) {
            contractName = request.getFileName();
        }

        Map<String, Object> reviewResult = aiService.reviewContract(
                contractName,
                request.getContractType(),
                request.getContent(),
                request.getReviewMode()
        );

        Contract contract = Contract.builder()
                .user(user)
                .contractName(contractName)
                .contractType(request.getContractType())
                .content(request.getContent())
                .reviewResult(reviewResult)
                .build();

        contractRepository.save(contract);

        Map<String, Object> result = new HashMap<>();
        result.put("id", contract.getId());
        result.put("reviewResult", reviewResult);

        return result;
    }

    public List<Map<String, Object>> getUserContracts(Long userId) {
        return contractRepository.findByUserIdOrderByCreatedAtDesc(userId)
                .stream()
                .map(this::toMap)
                .toList();
    }

    private Map<String, Object> toMap(Contract contract) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", contract.getId());
        map.put("contractName", contract.getContractName());
        map.put("contractType", contract.getContractType());
        map.put("createdAt", contract.getCreatedAt() != null ?
                contract.getCreatedAt().toString() : "");
        return map;
    }
}
