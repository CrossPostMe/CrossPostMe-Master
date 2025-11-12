// Apply the necessary plugins for Android, Kotlin, and Hilt.
// The 'kotlin-kapt' plugin is essential for Hilt's code generation.
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    // id("com.google.dagger.hilt.android") // Temporarily disabled
    // id("kotlin-kapt") // Temporarily disabled to test build
    id("kotlin-parcelize") // Enables @Parcelize annotation for data classes
}

android {
    namespace = "com.crosspostme" // IMPORTANT: Make sure this matches your project's package name
    compileSdk = 34

    defaultConfig {
        applicationId = "com.crosspostme"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }

        // API Configuration moved to buildTypes for per-environment values
    }

    buildTypes {
        debug {
            // Local dev API (cleartext allowed via network security config if needed)
            buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:8000/api/\"")
        }
        release {
            // Enforce secure API for production
            buildConfigField("String", "API_BASE_URL", "\"https://api.example.com/api/\"")
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_21
        targetCompatibility = JavaVersion.VERSION_21
    }
    kotlinOptions {
        jvmTarget = "21"
    }
    buildFeatures {
        compose = true
        buildConfig = true
    }
    composeOptions {
        // Align Compose compiler with modern Kotlin/Compose
        kotlinCompilerExtensionVersion = "1.5.11"
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

// This is the dependencies block where the main fix is applied.
dependencies {
    // OkHttp for networking and logging interceptor
    implementation("com.squareup.okhttp3:okhttp:4.10.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.10.0")

    // Core Android, Lifecycle, and Compose libraries
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.activity:activity-compose:1.8.2")
    implementation(platform("androidx.compose:compose-bom:2024.06.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")

    // Material3 and Google Material for theme compatibility
    implementation("androidx.compose.material3:material3:1.2.0")
    implementation("com.google.android.material:material:1.12.0")

    // Navigation Compose
    implementation("androidx.navigation:navigation-compose:2.7.7")

    // Lifecycle Compose
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.7.0")

    // Hilt DI
    implementation("com.google.dagger:hilt-android:2.48")
    // kapt("com.google.dagger:hilt-compiler:2.48")

    // Networking: Retrofit + Gson (switched from Moshi to avoid kapt issues)
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.10.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.10.0")

    // Database: Room
    implementation("androidx.room:room-runtime:2.6.1")
    // kapt("androidx.room:room-compiler:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")

    // Parcelize (already enabled via plugin)

    // Kotlin Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")

    // Lifecycle extensions
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0")
    implementation("androidx.lifecycle:lifecycle-livedata-ktx:2.7.0")
    // lifecycle-runtime-compose already added above; keep single declaration

    // No kapt needed for Retrofit itself

    // Testing libraries
    testImplementation("junit:junit:4.13.2")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation(platform("androidx.compose:compose-bom:2024.06.00"))
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
}

// This block is required by Kapt to configure Hilt's code generation.
// kapt {
//     correctErrorTypes = true
// }
