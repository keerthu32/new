import { useEffect, useState } from "react";
import { buyCattle, listCattle } from "../api";

export default function Buyer() {
  const [items, setItems] = useState([]);

  const load = async () => {
    const { data } = await listCattle();
    setItems(data);
  };

  const buy = async (id) => {
    await buyCattle(id);
    await load();
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <h2>Buyer Dashboard</h2>
      <ul>
        {items.map((c) => (
          <li key={c.id}>
            {c.title} | ${c.price} | Breed: {c.predicted_breed || "Unknown"} | Sold: {String(c.is_sold)}
            {!c.is_sold && <button onClick={() => buy(c.id)}>Buy (Dummy)</button>}
          </li>
        ))}
      </ul>
    </div>
  );
}
