<template>
    <div>
        <div class="header">
            <h1>🔥 Heat Map</h1>
            <div class="controls">
                <button @click="showLogin = !showLogin" v-if="!showLogin">
                    🔐 Login
                </button>
                <div v-if="showLogin" class="login-form">
                    <div class="form-group">
                        <label>Client Token:</label>
                        <input 
                            v-model="token" 
                            @keyup.enter="handleLogin"
                            placeholder="Enter your token"
                            type="text"
                        />
                    </div>
                    <button @click="handleLogin" class="btn-primary">Login</button>
                    <button @click="showLogin = false" class="btn-secondary">Cancel</button>
                </div>
                <button v-if="showLogin" @click="showAdmin = !showAdmin" class="btn-admin">
                    Admin Panel
                </button>
            </div>
        </div>
        
        <div class="admin-toggle">
            <button v-if="!showAdmin" @click="showAdmin = true" class="btn-admin">
                ⚙️ Admin
            </button>
            <button v-else @click="showAdmin = false" class="btn-admin">
                🔙 Back
            </button>
        </div>

        <div id="map" v-show="!showAdmin"></div>
        
        <div v-if="showAdmin" class="admin-container">
            <Admin />
        </div>
    </div>
</template>

<script>
import { onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.heatlayer'
import { fetchSubmissions, submitVibe } from '../api/client.js'
import Admin from './Admin.vue'

export default {
    name: 'MapView',
    components: { Admin },
    setup() {
        const showLogin = ref(false)
        const showAdmin = ref(false)
        const token = ref('')
        const clientToken = ref(null)
        const markers = ref([])
        const heatLayers = ref([])
        const map = ref(null)
        const heatLayer = ref(null)

        // Check URL for token parameter
        const urlParams = new URLSearchParams(window.location.search)
        const urlToken = urlParams.get('token')
        if (urlToken) {
            token.value = urlToken
            showLogin.value = true
        }

        // Initialize map
        const initMap = async () => {
            map.value = L.map('map').setView([39.8283, -98.5795], 3)

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map.value)

            await loadSubmissions()
            setInterval(loadSubmissions, 30000)
        }

        const loadSubmissions = async () => {
            try {
                const data = await fetchSubmissions()
                
                markers.value.forEach(m => {
                    if (m.layer) map.value.removeLayer(m.layer)
                })
                heatLayers.value.forEach(h => {
                    if (h.layer) map.value.removeLayer(h.layer)
                })
                markers.value = []
                heatLayers.value = []

                if (data.length === 0) return

                const heatData = data.map(d => [d.latitude, d.longitude, d.vibe_score / 5])
                heatLayer.value = L.heatLayer(heatData, {
                    radius: 5000,
                    blur: 25,
                    maxZoom: 10,
                    gradient: { 0.4: 'blue', 0.6: 'cyan', 0.7: 'cyan', 0.75: 'darkblue', 0.85: 'darkblue', 0.91: 'purple', 0.94: 'red', 1: 'red' }
                }).addTo(map.value)

                data.forEach(submission => {
                    const marker = L.marker([submission.latitude, submission.longitude])
                        .bindPopup(`
                            <strong>Vibe: ${submission.vibe_score}/5</strong><br/>
                            Time: ${new Date(submission.created_at).toLocaleString()}
                        `)
                        .openPopup()
                    map.value.addLayer(marker)
                    markers.value.push({ marker, data: submission })
                })

                if (data.length > 0) {
                    const bounds = L.latLngBounds(
                        data.map(d => [d.latitude, d.longitude])
                    )
                    map.value.fitBounds(bounds, { padding: [50, 50] })
                }
            } catch (error) {
                console.error('Error loading submissions:', error)
            }
        }

        const handleLogin = async () => {
            if (!token.value.trim()) return

            try {
                const response = await submitVibe(token.value.trim())
                clientToken.value = response.token
                showLogin.value = false
                token.value = ''
            } catch (error) {
                alert('Error: ' + (error.message || 'Failed to login'))
            }
        }

        const handleAddLocation = async () => {
            if (!clientToken.value) {
                alert('Please login first')
                return
            }

            try {
                // Use browser GPS
                if ('geolocation' in navigator) {
                    const position = await new Promise((resolve, reject) => {
                        navigator.geolocation.getCurrentPosition(resolve, reject, {
                            enableHighAccuracy: true,
                            timeout: 10000,
                            maximumAge: 0
                        })
                    })
                    
                    const lat = position.coords.latitude
                    const lng = position.coords.longitude
                    await submitVibeData(clientToken.value, lat, lng)
                } else {
                    alert('Geolocation not supported')
                }
            } catch (error) {
                console.error('Error adding location:', error)
                
                // Fallback to manual entry
                promptLocation()
            }
        }

        const promptLocation = () => {
            const lat = prompt('Enter latitude:')
            const lng = prompt('Enter longitude:')
            if (lat && lng) {
                submitVibeData(clientToken.value, parseFloat(lat), parseFloat(lng))
            }
        }

        const submitVibeData = async (token, latitude, longitude) => {
            const vibe = parseInt(prompt('Enter vibe score (1-5):'))
            if (isNaN(vibe) || vibe < 1 || vibe > 5) {
                alert('Please enter a valid vibe score between 1 and 5')
                return
            }

            try {
                const response = await submitVibe(token, latitude, longitude, vibe)
                if (response.success) {
                    alert('Location added successfully!')
                } else {
                    alert('Error: ' + response.message)
                }
            } catch (error) {
                alert('Error: ' + (error.message || 'Failed to submit location'))
            }
        }

        onMounted(() => {
            initMap()
        })

        return {
            showLogin,
            showAdmin,
            token,
            clientToken,
            handleLogin,
            handleAddLocation
        }
    }
}
</script>

<style scoped>
.header {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.95);
    padding: 1rem 2rem;
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.header h1 {
    margin: 0 0 0.5rem 0;
    color: #333;
}

.controls {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

.login-form {
    display: flex;
    gap: 0.5rem;
    align-items: flex-end;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.form-group label {
    font-size: 0.875rem;
    font-weight: 500;
    color: #666;
}

.form-group input {
    padding: 0.5rem 1rem;
    border: 2px solid #ddd;
    border-radius: 6px;
    font-size: 1rem;
    transition: border-color 0.2s;
}

.form-group input:focus {
    outline: none;
    border-color: #e74c3c;
}

.btn-primary, .btn-secondary, .btn-admin {
    padding: 0.5rem 1.25rem;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary {
    background: #e74c3c;
    color: white;
}

.btn-primary:hover {
    background: #c0392b;
}

.btn-secondary {
    background: #95a5a6;
    color: white;
}

.btn-secondary:hover {
    background: #7f8c8d;
}

.btn-admin {
    background: #34495e;
    color: white;
    font-size: 0.875rem;
    padding: 0.375rem 0.75rem;
}

.btn-admin:hover {
    background: #2c3e50;
}

.admin-toggle {
    position: absolute;
    top: 60px;
    right: 2rem;
    z-index: 1001;
}

.admin-container {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 2000;
    overflow-y: auto;
}

@media (max-width: 768px) {
    .header {
        padding: 0.75rem 1rem;
    }
    
    .header h1 {
        font-size: 1.5rem;
    }
    
    .controls {
        flex-wrap: wrap;
    }
    
    .login-form {
        flex-direction: column;
        align-items: stretch;
    }
    
    .form-group {
        align-items: flex-start;
    }
}
</style>
