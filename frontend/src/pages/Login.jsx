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
            // 1. Register/Login attempt
            const payload = { username, password: password || "123456" };

            // In a real app, this would be /login. Here we use existing /users/ create logic
            // If user exists (400), we proceed as login for MVP
            try {
                const res = await client.post('/users/', payload);
                localStorage.setItem('user_id', res.data.id);
                navigate('/dashboard');
            } catch (err) {
                if (err.response && err.response.status === 400) {
                    // User exists, just log in as user 1 for simulation or handle better
                    // Ideally we need a GET /users/search api. 
                    // For now, let's assume if 400, "Login Successful" for this MVP
                    localStorage.setItem('user_id', 1); // Simulation
                    navigate('/dashboard');
                } else {
                    setError('Connection Failed');
                }
            }
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="flex-center" style={{ height: '100vh' }}>
            <div className="card" style={{ width: '400px' }}>
                <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>🔐 SmartStudy Login</h2>

                {error && <div style={{ color: 'var(--danger)', marginBottom: '1rem' }}>{error}</div>}

                <form onSubmit={handleLogin}>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>

                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>

                    <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
                        Start Planning
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Login;
