# Étape 1 : Compilation avec Gradle
FROM gradle:8.7-jdk21-alpine AS BUILDER

WORKDIR /app

COPY . .

RUN gradle bootWar --no-daemon && \
    rm -rf ~/.gradle/caches && \
    rm -rf ~/.gradle/wrapper

# Étape 2 : Exécution sous Tomcat
FROM tomcat:10.1.24-jre21-temurin-jammy

WORKDIR $CATALINA_HOME/webapps

RUN rm -rf $CATALINA_HOME/webapps/*

COPY --from=BUILDER "/app/build/libs/*.war" "$CATALINA_HOME/webapps/ROOT.war"

EXPOSE 8080

CMD ["catalina.sh", "run"]