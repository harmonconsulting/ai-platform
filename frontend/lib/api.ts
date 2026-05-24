export const API_BASE =
process.env.NEXT_PUBLIC_API_URL ||
"http://100.69.108.88:8000/api/v1";

export async function sendMessage(message:string,conversationId?:number){
 const response=await fetch(`${API_BASE}/chat/`,{
   method:"POST",
   headers:{"Content-Type":"application/json"},
   body:JSON.stringify({
      message,
      provider:"ollama",
      model:"qwen2.5:7b",
      conversation_id:conversationId ?? null
   })
 });

 if(!response.ok) throw new Error("Chat request failed");
 return response.json();
}

export async function getConversation(id:number){
 const response=await fetch(`${API_BASE}/chat/${id}`);
 return response.json();
}

export async function getConversations(){
 const response=await fetch(`${API_BASE}/chat/conversations`);

 if(!response.ok) return [];

 const data=await response.json();

 return Array.isArray(data)
   ? data
   : [];
}

export async function uploadFile(file:File){
 const formData=new FormData();

 formData.append(
   "file",
   file
 );

 const response=await fetch(
   `${API_BASE}/upload/`,
   {
      method:"POST",
      body:formData
   }
 );

 if(!response.ok)
    throw new Error("Upload failed");

 return response.json();
}

export async function listUploads(){
 const response=await fetch(
   `${API_BASE}/upload/`
 );

 return response.json();
}

export async function deleteUpload(filename:string){
 const response=await fetch(
   `${API_BASE}/upload/${encodeURIComponent(filename)}`,
   {
      method:"DELETE"
   }
 );

 return response.json();
}

export async function reindexUploads(){
 const response=await fetch(
   `${API_BASE}/upload/reindex`,
   {
      method:"POST"
   }
 );

 return response.json();
}
