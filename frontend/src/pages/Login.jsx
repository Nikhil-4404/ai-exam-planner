import React, { useState } from 'react';
import client from '../api/client';
import { useNavigate } from 'react-router-dom';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const payload = { username, password: password || "123456" };
            try {
                const res = await client.post('/users/', payload);
                localStorage.setItem('user_id', res.data.id);
                navigate('/dashboard');
            } catch (err) {
                if (err.response && err.response.status === 400) {
                    // User exists logic
                    localStorage.setItem('user_id', 1);
                    navigate('/dashboard');
                } else if (err.code === "ERR_NETWORK") {
                    setError('Backend Unreachable. Ensure API is running on port 8000.');
                } else {
                    setError(err.response?.data?.detail || 'Connection Failed');
                }
            }
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="flex-center">
            <div className="card animate-enter" style={{ width: '100%', maxWidth: '400px', margin: '1rem' }}>
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔐</h1>
                    <h2>SmartStudy Login</h2>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                        Enter your credentials to access your planner.
                    </p>
                </div>

                {error && (
                    <div style={{
                        background: 'rgba(239, 68, 68, 0.1)',
                        color: '#fca5a5',
                        padding: '0.75rem',
                        borderRadius: 'var(--radius)',
                        marginBottom: '1.5rem',
                        textAlign: 'center',
                        fontSize: '0.9rem'
                    }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleLogin}>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            placeholder="e.g. Student1"
                        />
                    </div>

                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                        />
                    </div>

                    <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '1rem' }}>
                        Start Planning 🚀
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Login;
