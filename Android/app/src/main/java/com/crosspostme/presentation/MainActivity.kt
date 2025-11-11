package com.crosspostme.presentation

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.crosspostme.data.model.Ad
import com.crosspostme.presentation.viewmodel.AdsViewModel
import com.crosspostme.ui.theme.CrossPostMeTheme
import dagger.hilt.android.AndroidEntryPoint

/**
 * Main Activity for CrossPostMe app
 * Following Android Compose patterns and MVVM architecture
 */
@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    
    private val adsViewModel: AdsViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            CrossPostMeTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    CrossPostMeApp(adsViewModel = adsViewModel)
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CrossPostMeApp(adsViewModel: AdsViewModel) {
    val navController = rememberNavController()
    NavHost(navController = navController, startDestination = "dashboard") {
        composable("dashboard") {
            DashboardScreen(adsViewModel = adsViewModel, navController = navController)
        }
        composable("login") {
            LoginScreen(navController = navController)
        }
        composable("register") {
            RegisterScreen(navController = navController)
        }
        composable("ad_create") {
            AdCreateScreen(adsViewModel = adsViewModel, navController = navController)
        }
        composable("platform_management") {
            PlatformManagementScreen(navController = navController)
        }
        composable("messaging") {
            MessagingScreen(navController = navController)
        }
    }
}

@Composable
fun DashboardScreen(adsViewModel: AdsViewModel, navController: NavHostController) {
    val adsUiState by adsViewModel.adsUiState.collectAsStateWithLifecycle()
    val dashboardUiState by adsViewModel.dashboardUiState.collectAsStateWithLifecycle()
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "CrossPostMe Dashboard",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 16.dp)
        )
        dashboardUiState.stats?.let { stats ->
            DashboardStatsCard(
                stats = stats,
                modifier = Modifier.padding(bottom = 16.dp)
            )
        }
        Button(onClick = { navController.navigate("ad_create") }, modifier = Modifier.padding(bottom = 8.dp)) {
            Text("Create New Ad")
        }
        Button(onClick = { navController.navigate("platform_management") }, modifier = Modifier.padding(bottom = 8.dp)) {
            Text("Manage Platforms")
        }
        Button(onClick = { navController.navigate("messaging") }, modifier = Modifier.padding(bottom = 8.dp)) {
            Text("Messaging & Leads")
        }
        Button(onClick = { navController.navigate("login") }, modifier = Modifier.padding(bottom = 8.dp)) {
            Text("Login")
        }
        Button(onClick = { navController.navigate("register") }, modifier = Modifier.padding(bottom = 8.dp)) {
            Text("Register")
        }
        Text(
            text = "Your Ads",
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.SemiBold,
            modifier = Modifier.padding(bottom = 8.dp)
        )
        // ...existing ad list UI...
    }
}

@Composable
fun LoginScreen(navController: NavHostController) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }
    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("Login", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") },
            modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp)
        )
        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
            visualTransformation = PasswordVisualTransformation()
        )
        error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        Button(
            onClick = {
                if (email.isBlank() || password.isBlank()) {
                    error = "Email and password required"
                } else {
                    // TODO: Connect to repository for login
                    navController.navigate("dashboard")
                }
            },
            modifier = Modifier.padding(top = 16.dp)
        ) { Text("Login") }
    }
}

@Composable
fun RegisterScreen(navController: NavHostController) {
    var email by remember { mutableStateOf("") }
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var error by remember { mutableStateOf<String?>(null) }
    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("Register", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        OutlinedTextField(
            value = username,
            onValueChange = { username = it },
            label = { Text("Username") },
            modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp)
        )
        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") },
            modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp)
        )
        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
            visualTransformation = PasswordVisualTransformation()
        )
        error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        Button(
            onClick = {
                if (email.isBlank() || password.isBlank() || username.isBlank()) {
                    error = "All fields required"
                } else {
                    // TODO: Connect to repository for registration
                    navController.navigate("dashboard")
                }
            },
            modifier = Modifier.padding(top = 16.dp)
        ) { Text("Register") }
    }
}

@Composable
fun AdCreateScreen(adsViewModel: AdsViewModel, navController: NavHostController) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("Create/Edit Ad", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        // ...ad creation/edit form UI...
        Button(onClick = { navController.navigate("dashboard") }) { Text("Save Ad") }
    }
}

@Composable
fun PlatformManagementScreen(navController: NavHostController) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("Platform Management", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        // ...platform account management UI...
        Button(onClick = { navController.navigate("dashboard") }) { Text("Back to Dashboard") }
    }
}

@Composable
fun MessagingScreen(navController: NavHostController) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text("Messaging & Leads", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        // ...messaging and leads UI...
        Button(onClick = { navController.navigate("dashboard") }) { Text("Back to Dashboard") }
    }
}
        if (adsUiState.isLoading) {
            Box(
                modifier = Modifier.fillMaxWidth(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        }
        
        // Error state
        adsUiState.error?.let { error ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 8.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.errorContainer
                )
            ) {
                Text(
                    text = error,
                    color = MaterialTheme.colorScheme.onErrorContainer,
                    modifier = Modifier.padding(16.dp)
                )
            }
        }
        
        // Ads List
        LazyColumn {
            items(adsUiState.ads) { ad ->
                AdCard(
                    ad = ad,
                    onAdClick = { adsViewModel.selectAd(ad) },
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }
        }
    }
}

@Composable
fun DashboardStatsCard(
    stats: com.crosspostme.data.model.DashboardStats,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Dashboard",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.padding(bottom = 8.dp)
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                StatItem(label = "Total Ads", value = stats.totalAds.toString())
                StatItem(label = "Active", value = stats.activeAds.toString())
                StatItem(label = "Platforms", value = stats.platformsConnected.toString())
            }
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                StatItem(label = "Posts", value = stats.totalPosts.toString())
                StatItem(label = "Views", value = stats.totalViews.toString())
                StatItem(label = "Leads", value = stats.totalLeads.toString())
            }
        }
    }
}

@Composable
fun StatItem(label: String, value: String) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AdCard(
    ad: Ad,
    onAdClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        onClick = onAdClick,
        modifier = modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = ad.title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )
            
            Text(
                text = "$${ad.price}",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(vertical = 4.dp)
            )
            
            Text(
                text = ad.description,
                style = MaterialTheme.typography.bodyMedium,
                maxLines = 2,
                modifier = Modifier.padding(bottom = 8.dp)
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Status: ${ad.status}",
                    style = MaterialTheme.typography.bodySmall
                )
                
                Text(
                    text = ad.category,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.secondary
                )
            }
        }
    }
}