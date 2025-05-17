plugins {
    id("java")
    id("com.github.johnrengelman.shadow") version "7.1.2"
    application
}

group = "com.zjt"
version = "1.0"

application {
    mainClass.set("com.zjt.Main")
}
repositories {
    mavenCentral()
}

dependencies {
    testImplementation(platform("org.junit:junit-bom:5.10.0"))
    testImplementation("org.junit.jupiter:junit-jupiter")
    implementation("com.google.code.gson:gson:2.8.9")
}

tasks.test {
    useJUnitPlatform()
}

tasks.jar {
    manifest {
        attributes(
            "Main-Class" to "com.zjt.Main" // 指定主类
        )
    }
}

tasks.shadowJar {
    archiveBaseName.set("maze") // 自定义输出 JAR 文件名
    archiveVersion.set("1.0.0")      // 自定义版本号
    archiveClassifier.set("all")     // 表示这是包含依赖的 Fat JAR
}


tasks.shadowJar {
    minimize()

    // 排除不需要的文件（可选）
    exclude("META-INF/*.SF")
    exclude("META-INF/*.DSA")
    exclude("META-INF/*.RSA")


    manifest {
        attributes(
            "Main-Class" to "com.zjt.Main" // 指定主类
        )
    }
}

