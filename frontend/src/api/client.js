export const API_BASE = '/api'

export async function submitVibe(token, latitude, longitude, vibe) {
    const response = await fetch(`${API_BASE}/submission`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: token,
            latitude: latitude,
            longitude: longitude,
            vibe_score: vibe
        })
    })

    const data = await response.json()
    return data
}

export async function fetchSubmissions() {
    const response = await fetch(`${API_BASE}/submissions`)
    if (!response.ok) {
        throw new Error('Failed to fetch submissions')
    }
    return response.json()
}

export async function checkHealth() {
    const response = await fetch(`${API_BASE}/health`)
    return response.ok
}

export async function fetchAllTokens() {
    const response = await fetch(`${API_BASE}/tokens`)
    if (!response.ok) {
        throw new Error('Failed to fetch tokens')
    }
    return response.json()
}

export async function generateToken() {
    const response = await fetch(`${API_BASE}/admin/generate`, {
        method: 'POST'
    })
    if (!response.ok) {
        throw new Error('Failed to generate token')
    }
    return response.json()
}

export async function deleteToken(token) {
    const response = await fetch(`${API_BASE}/admin/delete`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token })
    })
    if (!response.ok) {
        throw new Error('Failed to delete token')
    }
    return response.json()
}
