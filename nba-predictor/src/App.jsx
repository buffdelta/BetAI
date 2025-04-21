import { useEffect, useState } from 'react';

function App() {
    const [teams, setTeams] = useState([]);
    const [team1, setTeam1] = useState('');
    const [team2, setTeam2] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    console.log("Result object:", result)

    useEffect(() => {
        fetch('https://betai.onrender.com/teams')
        .then(res => res.json())
        .then(setTeams)
        .catch(err => console.error('Failed to fetch teams:', err));
        }, []);

    const handlePredict = async() => {
        if (!team1 || !team2) {
            alert("Please select both teams.");
            return;
            }
        if (team1 === team2) {
            alert("Please select two different teams.");
            return;
            }
        try {
            setLoading(true);
            setResult(null);

            const res = await fetch(`https://betai.onrender.com/predict?team1=${team1}&team2=${team2}`);
            const data = await res.json();

            if (data.error) {
                alert(data.error);
                } else {
                    setResult(data);
                    setTeam1('');
                    setTeam2('');
                }
        } catch (ex) {
                console.error("Prediction Failed: ", ex);
                alert("Something went wrong. Try Again.");
        } finally {
            setLoading(false);
            }
    };
    return (
        <div style = {{padding: '2rem', textAlign: 'center'}}>
            <h1>NBA Match-up Predictor</h1>

            <div style = {{marginBottom: '1rem'}}>
                <label>
                    Team 1:
                    <select value = {team1} onChange = {e => setTeam1(e.target.value)} style = {{marginLeft: '0.5rem'}}>
                        <option value = " ">select</option>
                        {teams.map(team => (
                            <option key = {team} value = {team}>{team}</option>
                            ))}
                    </select>
                </label>

                <label style = {{ marginLeft: '2rem'}}>
                    Team 2:
                    <select value = {team2} onChange = {e => setTeam2(e.target.value)} style = {{marginLeft: '0.5rem'}}>
                        <option value = " ">select</option>
                        {teams.map(team => (
                            <option key = {team} value = {team}>{team}</option>
                            ))}
                    </select>
                </label>
            </div>

            <button onClick = {handlePredict}>Predict</button>

            {result && (
                <h2 style = {{marginTop: '2rem'}}>
                    Predicted Winner: {result.predicted_winner}<br />
                    ({team1}: {result.team1_avg_pts} pts, {team2}: {result.team2_avg_pts} pts)
                </h2>
                )}
            </div>
        );
    }

export default App;