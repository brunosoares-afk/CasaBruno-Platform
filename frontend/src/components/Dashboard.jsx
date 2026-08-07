import {useEffect,useState} from "react";
import api from "../services/api";
import StatusCard from "./StatusCard";

export default function Dashboard(){

    const [status,setStatus]=useState(null);

    useEffect(()=>{

        api.get("/api/status")
        .then(r=>setStatus(r.data))
        .catch(console.error);

    },[]);

    if(!status){

        return <h2>Carregando...</h2>

    }

    return(

        <div className="dashboard">

            <StatusCard
                titulo="CPU"
                valor={status.cpu_percent+" %"}
            />

            <StatusCard
                titulo="RAM"
                valor={status.memory_percent+" %"}
            />

            <StatusCard
                titulo="Disco"
                valor={status.disk_percent+" %"}
            />

            <StatusCard
                titulo="Hostname"
                valor={status.hostname}
            />

        </div>

    );

}
