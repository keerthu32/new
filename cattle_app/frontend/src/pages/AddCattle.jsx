import { useState } from "react";
import { addCattle } from "../api";

export default function AddCattle({ onDone }) {
  const [title, setTitle] = useState("");
  const [price, setPrice] = useState("");
  const [image, setImage] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("title", title);
    formData.append("price", price);
    formData.append("image", image);
    await addCattle(formData);
    setTitle("");
    setPrice("");
    setImage(null);
    onDone?.();
  };

  return (
    <form onSubmit={submit}>
      <h3>Add Cattle + ML Breed</h3>
      <input value={title} placeholder="Title" onChange={(e) => setTitle(e.target.value)} />
      <input value={price} placeholder="Price" type="number" onChange={(e) => setPrice(e.target.value)} />
      <input type="file" accept="image/*" onChange={(e) => setImage(e.target.files[0])} />
      <button type="submit">Upload</button>
    </form>
  );
}
