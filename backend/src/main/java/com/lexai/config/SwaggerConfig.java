package com.lexai.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SwaggerConfig {

    @Bean
    public OpenAPI openAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("LexAI 法律智能体平台 API")
                        .description("智慧法律咨询、案件分析、合同审查、文书生成")
                        .version("1.0.0"));
    }
}
