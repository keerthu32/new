import { useEffect, useState } from "react";
import { getNotifications } from "../api";
import AddCattle from "./AddCattle";

export default function Seller() {
  const [notes, setNotes] = useState([]);

  const loadNotes = async () => {
    const { data } = await getNotifications();
    setNotes(data);
  };

  useEffect(() => {
    loadNotes();
  }, []);

  return (
    <div>
      <h2>Seller Dashboard</h2>
      <AddCattle onDone={loadNotes} />
      <h3>Notifications</h3>
      <ul>
        {notes.map((n) => (
          <li key={n.id}>{n.message}</li>
        ))}
      </ul>
    </div>
  );
}
