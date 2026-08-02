<template>
    <div class="admin-panel">
        <div class="container">
            <h1>🔥 Heat Map Admin</h1>
            
            <div class="card">
                <h2>Generate Client Tokens</h2>
                <p class="description">Generate unique tokens for clients to access the heat map</p>
                <button @click="generateToken" class="btn-primary">Generate New Token</button>
                <div v-if="generatedToken" class="token-display">
                    <label>Token:</label>
                    <input :value="generatedToken" readonly class="token-input" />
                    <button @click="copyToken" class="btn-secondary">Copy</button>
                </div>
                <div v-if="message.text" :class="['message', message.type]">{{ message.text }}</div>
            </div>

            <div class="card">
                <h2>Active Tokens</h2>
                <p class="description">List of all tokens that have been used</p>
                <button @click="loadTokens" class="btn-secondary" v-if="!loadingTokens">Refresh</button>
                <button v-else class="btn-secondary">Loading...</button>
                
                <div v-if="tokens.length === 0" class="empty-state">
                    No tokens found. Generate one first!
                </div>
                <div v-else class="token-list">
                    <table>
                        <thead>
                            <tr>
                                <th>Token</th>
                                <th>Usage</th>
                                <th>First Seen</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="token in tokens" :key="token.token">
                                <td>
                                    <code>{{ token.token }}</code>
                                    <button @click="copyToken(token.token)" class="btn-small">Copy</button>
                                </td>
                                <td>{{ token.usage_count }} submissions</td>
                                <td>{{ formatDate(token.first_seen) }}</td>
                                <td>
                                    <button @click="deleteToken(token.token)" class="btn-danger">Remove</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="card">
                <h2>Quick Start</h2>
                <div class="instructions">
                    <ol>
                        <li>Generate a token for your client</li>
                        <li>Copy the token</li>
                        <li>Share with client: <code>http://localhost:3000/login?token=YOUR_TOKEN</code></li>
                        <li>Client will see their location on the heat map</li>
                    </ol>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import {
    fetchAllTokens,
    generateToken as apiGenerateToken,
    deleteToken as apiDeleteToken
} from './api/client.js'

export default {
    name: 'AdminPanel',
    setup() {
        const generatedToken = ref('')
        const tokens = ref([])
        const loadingTokens = ref(false)
        const message = ref({ type: '', text: '' })

        const generateToken = async () => {
            try {
                const data = await apiGenerateToken()
                generatedToken.value = data.token
                message.value = { type: 'success', text: 'Token generated successfully!' }
                setTimeout(() => {
                    message.value = { type: '', text: '' }
                }, 3000)
            } catch (error) {
                message.value = { type: 'error', text: 'Failed to generate token: ' + error.message }
            }
        }

        const loadTokens = async () => {
            loadingTokens.value = true
            try {
                const data = await fetchAllTokens()
                tokens.value = data.tokens.map(token => ({
                    token,
                    usage_count: 1,
                    first_seen: new Date().toISOString()
                }))
            } catch (error) {
                message.value = { type: 'error', text: 'Failed to load tokens: ' + error.message }
            }
            loadingTokens.value = false
        }

        const copyToken = async (token) => {
            await navigator.clipboard.writeText(token)
            message.value = { type: 'success', text: 'Token copied to clipboard!' }
            setTimeout(() => {
                message.value = { type: '', text: '' }
            }, 2000)
        }

        const deleteToken = async (token) => {
            if (!confirm(`Delete token: ${token}?`)) return
            
            try {
                await apiDeleteToken(token)
                message.value = { type: 'success', text: 'Token deleted successfully!' }
                setTimeout(() => {
                    message.value = { type: '', text: '' }
                }, 2000)
                loadTokens()
            } catch (error) {
                message.value = { type: 'error', text: 'Failed to delete token: ' + error.message }
            }
        }

        const formatDate = (dateString) => {
            return new Date(dateString).toLocaleString()
        }

        onMounted(() => {
            loadTokens()
        })

        return {
            generatedToken,
            tokens,
            loadingTokens,
            message,
            generateToken,
            loadTokens,
            copyToken,
            deleteToken,
            formatDate
        }
    }
}
</script>

<style scoped>
.admin-panel {
    width: 100vw;
    height: 100vh;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    padding: 2rem;
    overflow-y: auto;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

h1 {
    text-align: center;
    color: #fff;
    margin-bottom: 2rem;
    font-size: 2.5rem;
}

.card {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(10px);
}

.card h2 {
    color: #fff;
    margin-bottom: 0.5rem;
    font-size: 1.5rem;
}

.description {
    color: #ccc;
    margin-bottom: 1rem;
}

.instructions {
    background: rgba(0, 0, 0, 0.2);
    padding: 1rem;
    border-radius: 8px;
}

.instructions ol {
    margin: 0;
    padding-left: 1.5rem;
    color: #ccc;
}

.instructions li {
    margin-bottom: 0.5rem;
}

.instructions code {
    background: #333;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    color: #fff;
    font-family: monospace;
}

.btn-primary, .btn-secondary, .btn-danger, .btn-small {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
    margin-right: 0.5rem;
}

.btn-primary {
    background: #e74c3c;
    color: white;
}

.btn-primary:hover {
    background: #c0392b;
}

.btn-secondary {
    background: #3498db;
    color: white;
}

.btn-secondary:hover {
    background: #2980b9;
}

.btn-danger {
    background: #e74c3c;
    color: white;
}

.btn-danger:hover {
    background: #c0392b;
}

.btn-small {
    padding: 0.25rem 0.5rem;
    font-size: 0.875rem;
    background: #3498db;
    color: white;
}

.btn-small:hover {
    background: #2980b9;
}

.token-display {
    margin-top: 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.token-input {
    flex: 1;
    padding: 0.75rem;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid #444;
    border-radius: 6px;
    color: #fff;
    font-family: monospace;
    font-size: 1rem;
}

.token-input:focus {
    outline: none;
    border-color: #e74c3c;
}

.message {
    margin-top: 1rem;
    padding: 0.75rem 1rem;
    border-radius: 6px;
}

.message.success {
    background: rgba(46, 204, 113, 0.2);
    color: #2ecc71;
}

.message.error {
    background: rgba(231, 76, 60, 0.2);
    color: #e74c3c;
}

.empty-state {
    text-align: center;
    color: #ccc;
    padding: 2rem;
}

.token-list {
    margin-top: 1rem;
}

.token-list table {
    width: 100%;
    border-collapse: collapse;
}

.token-list th,
.token-list td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.token-list th {
    color: #fff;
    font-weight: 600;
}

.token-list code {
    background: rgba(0, 0, 0, 0.3);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-family: monospace;
    color: #e74c3c;
}

@media (max-width: 768px) {
    .admin-panel {
        padding: 1rem;
    }
    
    h1 {
        font-size: 2rem;
    }
    
    .card {
        padding: 1rem;
    }
    
    .token-display {
        flex-direction: column;
        align-items: stretch;
    }
    
    .token-list table {
        display: block;
        overflow-x: auto;
    }
}
</style>
