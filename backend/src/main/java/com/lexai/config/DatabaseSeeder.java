package com.lexai.config;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.dao.DataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.init.ResourceDatabasePopulator;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Objects;

@Slf4j
@Component
@RequiredArgsConstructor
public class DatabaseSeeder implements CommandLineRunner {

    private final DataSource dataSource;
    private final JdbcTemplate jdbcTemplate;

    @Override
    public void run(String... args) {
        if (hasSeedData()) {
            log.info("Case library already has data, skip seed script on startup.");
            return;
        }

        Resource script = resolveSeedScript();
        if (script == null || !script.exists()) {
            log.warn("Seed script not found, skip auto import.");
            return;
        }

        ResourceDatabasePopulator populator = new ResourceDatabasePopulator();
        populator.addScript(script);
        populator.setContinueOnError(false);
        populator.setSeparator(";");
        populator.setCommentPrefixes("--");
        populator.execute(Objects.requireNonNull(dataSource));

        log.info("Case library seed script executed successfully in incremental mode.");
    }

    private boolean hasSeedData() {
        try {
            Integer count = jdbcTemplate.queryForObject("SELECT COUNT(1) FROM case_library", Integer.class);
            return count != null && count > 0;
        } catch (DataAccessException ex) {
            // Table may not exist on first startup; run script to initialize schema and seed data.
            log.info("case_library table not ready, will execute seed script. reason={}", ex.getMessage());
            return false;
        }
    }

    private Resource resolveSeedScript() {
        Resource classpathResource = new ClassPathResource("database/schema.sql");
        if (classpathResource.exists()) {
            return classpathResource;
        }

        Path workingDirectory = Paths.get(System.getProperty("user.dir")).toAbsolutePath();
        Path repositoryRoot = workingDirectory.getParent();
        if (repositoryRoot != null) {
            Path externalScript = repositoryRoot.resolve("database").resolve("schema.sql");
            Resource fileResource = new FileSystemResource(Objects.requireNonNull(externalScript));
            if (fileResource.exists()) {
                return fileResource;
            }
        }

        return null;
    }
}