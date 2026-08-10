package com.lexai.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class SiliconFlowConfig {

    @Value("${siliconflow.api.key}")
    private String apiKey;

    @Value("${siliconflow.api.base-url}")
    private String baseUrl;

    @Value("${siliconflow.model}")
    private String model;

    @Bean
    public RestTemplate siliconFlowRestTemplate() {
        return new RestTemplate();
    }

    public String getApiKey() {
        return apiKey;
    }

    public String getBaseUrl() {
        return baseUrl;
    }

    public String getModel() {
        return model;
    }
}
