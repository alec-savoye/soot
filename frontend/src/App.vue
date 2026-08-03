<template>
    <div>
        <div class="header">
            <h1>🔥 Heat Map</h1>
            <div class="controls">
                <button @click="showLogin = !showLogin" v-if="!showLogin && !clientToken">
                    🔐 Login
                </button>
                <button v-if="clientToken" @click="handleAddLocation" class="btn-primary">
                    📍 Add my location
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
import { onMounted, ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.heat'
import { fetchSubmissions, submitVibe } from './api/client.js'
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

        // Initialize map with NYC as default view
        const initMap = async () => {
            map.value = L.map('map').setView([40.7128, -74.0060], 11)

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map.value)

            await loadSubmissions()
            setInterval(loadSubmissions, 30000)
        }

        const loadSubmissions = async () => {
            try {
                const result = await fetchSubmissions()
                const data = result.data || []
                
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

        const handleLogin = () => {
            if (!token.value.trim()) return

            // Token-based auth is stateless: just remember the token locally.
            clientToken.value = token.value.trim()
            showLogin.value = false
            token.value = ''
        }

        const handleAddLocation = async () => {
            if (!clientToken.value) {
                alert('Please login first')
                return
            }

            try {
                const address = prompt('Enter your NYC area (e.g., "Times Square", "Central Park", "Brooklyn", "Manhattan", "Queens"):')
                if (!address) return

                const vibe = parseInt(prompt('Enter vibe score (1-5):'))
                if (isNaN(vibe) || vibe < 1 || vibe > 5) {
                    alert('Please enter a valid vibe score between 1 and 5')
                    return
                }

                const geo = await fetchAreaCoordinates(address)
                if (!geo) return

                await submitVibeData(clientToken.value, geo.lat, geo.lng)
            } catch (error) {
                console.error('Error adding location:', error)
            }
        }

        async function fetchAreaCoordinates(area) {
            // Predefined NYC area coordinates
            const areas = {
                'Times Square': { lat: 40.7580, lng: -73.9855 },
                'Central Park': { lat: 40.7829, lng: -73.9654 },
                'Brooklyn': { lat: 40.6782, lng: -73.9442 },
                'Manhattan': { lat: 40.7831, lng: -73.9712 },
                'Queens': { lat: 40.7282, lng: -73.7949 },
                'Staten Island': { lat: 40.5795, lng: -74.1502 },
                'Bronx': { lat: 40.8448, lng: -73.8648 },
                'Financial District': { lat: 40.7074, lng: -74.0113 },
                'Upper East Side': { lat: 40.7736, lng: -73.9566 },
                'Upper West Side': { lat: 40.7870, lng: -73.9754 },
                'Chelsea': { lat: 40.7465, lng: -74.0014 },
                'Williamsburg': { lat: 40.7081, lng: -73.9571 },
                'SoHo': { lat: 40.7233, lng: -74.0030 },
                'Greenwich Village': { lat: 40.7336, lng: -74.0027 },
                'East Village': { lat: 40.7264, lng: -73.9817 },
                'Harlem': { lat: 40.8116, lng: -73.9465 },
                'The Bronx': { lat: 40.8448, lng: -73.8648 },
                'Bay Ridge': { lat: 40.6345, lng: -74.0247 },
                'Astoria': { lat: 40.7720, lng: -73.9230 },
                'Coney Island': { lat: 40.5755, lng: -73.9707 },
                'Rockefeller Center': { lat: 40.7587, lng: -73.9787 },
                'Empire State Building': { lat: 40.7484, lng: -73.9857 },
                'Top of the Rock': { lat: 40.7590, lng: -73.9794 },
                'One World Trade Center': { lat: 40.7127, lng: -74.0134 },
                'High Line': { lat: 40.7480, lng: -74.0048 },
                'Museums District': { lat: 40.7794, lng: -73.9632 },
                'Madison Square Garden': { lat: 40.7505, lng: -73.9934 },
                'Grand Central Terminal': { lat: 40.7527, lng: -73.9772 }
            }

            // Try exact match first
            if (areas[area]) {
                return areas[area]
            }

            // Fallback to Manhattan center if unknown
            alert('Unknown area. Defaulting to Manhattan.')
            return { lat: 40.7831, lng: -73.9712 }
        }

        const submitVibeData = async (token, latitude, longitude) => {
            try {
                const response = await submitVibe(token, latitude, longitude, 3)
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
            handleAddLocation,
            submitVibeData
        }
    }
}
</script>

<style scoped>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    overflow: hidden;
}

#app {
    width: 100vw;
    height: 100vh;
    position: relative;
}

.header {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem 2.5rem;
    z-index: 1000;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header h1 {
    margin: 0;
    font-size: 2rem;
    color: white;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.header h1::after {
    content: '';
    display: block;
    width: 4px;
    height: 2rem;
    background: #ff6b6b;
    border-radius: 2px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scaleY(1); }
    50% { opacity: 0.7; transform: scaleY(0.9); }
}

.controls {
    display: flex;
    gap: 0.75rem;
    align-items: center;
    flex-wrap: wrap;
}

.login-form {
    display: flex;
    gap: 0.75rem;
    align-items: flex-end;
    background: white;
    padding: 0.75rem 1rem;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.form-group label {
    font-size: 0.875rem;
    font-weight: 600;
    color: #667eea;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.form-group input {
    padding: 0.625rem 1rem;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    transition: all 0.3s ease;
    background: #f8f9fa;
}

.form-group input:focus {
    outline: none;
    border-color: #667eea;
    background: white;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn-primary, .btn-secondary, .btn-admin {
    padding: 0.625rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-size: 0.9375rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.btn-primary {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.5);
}

.btn-primary:active {
    transform: translateY(0);
}

.btn-secondary {
    background: linear-gradient(135deg, #a8c0ff 0%, #3f2b96 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(63, 43, 150, 0.3);
}

.btn-secondary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(63, 43, 150, 0.4);
}

.btn-admin {
    background: transparent;
    color: #667eea;
    border: 2px solid #667eea;
    font-size: 0.8125rem;
    padding: 0.5rem 1rem;
}

.btn-admin:hover {
    background: rgba(102, 126, 234, 0.1);
    transform: translateY(-2px);
}

.admin-toggle {
    position: absolute;
    top: 80px;
    right: 2rem;
    z-index: 1001;
}

.map-container {
    width: 100%;
    height: calc(100vh - 80px);
    background: #e8f4f8;
}

#map {
    width: 100%;
    height: 100%;
}

@media (max-width: 768px) {
    .header {
        padding: 1rem 1.25rem;
        flex-direction: column;
        gap: 1rem;
    }

    .header h1 {
        font-size: 1.5rem;
    }

    .controls {
        width: 100%;
        justify-content: center;
    }

    .login-form {
        width: 100%;
        flex-direction: column;
        align-items: stretch;
    }

    .form-group {
        width: 100%;
    }

    .form-group input {
        width: 100%;
    }

    .btn-primary, .btn-secondary, .btn-admin {
        width: 100%;
        justify-content: center;
    }
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
        padding: 1rem 1.25rem;
        flex-direction: column;
        gap: 1rem;
    }

    .header h1 {
        font-size: 1.5rem;
    }

    .controls {
        width: 100%;
        justify-content: center;
    }

    .login-form {
        width: 100%;
        flex-direction: column;
        align-items: stretch;
    }

    .form-group {
        width: 100%;
    }

    .form-group input {
        width: 100%;
    }

    .btn-primary, .btn-secondary, .btn-admin {
        width: 100%;
        justify-content: center;
    }
}
</style>
