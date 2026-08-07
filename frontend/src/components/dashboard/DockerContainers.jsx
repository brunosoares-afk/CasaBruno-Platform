import {
Card,
CardContent,
Typography,
List,
ListItem,
Chip
} from "@mui/material";

export default function DockerContainers({ containers }) {

return(

<Card
sx={{
background:"#1e293b",
color:"white",
borderRadius:3
}}
>

<CardContent>

<Typography variant="h6">

Containers Docker

</Typography>

<List>

{containers.map((c)=>(
<ListItem
key={c}
sx={{
display:"flex",
justifyContent:"space-between"
}}
>

{c}

<Chip
label="ONLINE"
color="success"
size="small"
/>

</ListItem>
))}

</List>

</CardContent>

</Card>

)

}
