FROM maven:3.9.9-eclipse-temurin-17 AS builder

WORKDIR /workspace

COPY pom.xml .
RUN mvn -B dependency:go-offline

COPY src ./src
RUN mvn -B package -DskipTests

FROM eclipse-temurin:17-jre

WORKDIR /app

COPY --from=builder /workspace/target/quarkus-app/lib/ ./lib/
COPY --from=builder /workspace/target/quarkus-app/*.jar ./
COPY --from=builder /workspace/target/quarkus-app/app/ ./app/
COPY --from=builder /workspace/target/quarkus-app/quarkus/ ./quarkus/

EXPOSE 8080

CMD ["java", "-Dquarkus.http.host=0.0.0.0", "-Dquarkus.http.port=8080", "-jar", "quarkus-run.jar"]
