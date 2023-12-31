import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://acit3855kafkazoo.eastus2.cloudapp.azure.com/health_check/health`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); 
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
            <h1>Health Status</h1>
            <p><strong>Receiver:</strong> {stats['Receiver']}</p>
            <p><strong>Storage:</strong> {stats['Storage']}</p>
            <p><strong>Processing:</strong> {stats['Processing']}</p>
            <p><strong>Audit:</strong> {stats['Audit']}</p>
            <p><strong>Last Update:</strong> {stats['last_update']}</p>
            </div>
        )
    }
}
