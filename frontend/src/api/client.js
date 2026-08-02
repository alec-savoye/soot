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
