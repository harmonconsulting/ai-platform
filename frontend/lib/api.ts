export const API_BASE =
process.env.NEXT_PUBLIC_API_URL ||
"http://100.69.108.88:8000/api/v1";


function getToken(){
   if(typeof window==="undefined")
      return null;

   return localStorage.getItem("token");
}


function authHeaders(extra:any={}){

   const token=getToken();

   return {
      ...extra,
      ...(token
         ? {Authorization:`Bearer ${token}`}
         : {}
      )
   };
}


export async function login(
   email:string,
   password:string
){

   const response=await fetch(
      `${API_BASE}/auth/login`,
      {
         method:"POST",
         headers:{
            "Content-Type":"application/json"
         },
         body:JSON.stringify({
            email,
            password
         })
      }
   );

   if(!response.ok)
      throw new Error("Login failed");

   const data=await response.json();

   localStorage.setItem(
      "token",
      data.access_token
   );

   return data;
}


export function logout(){

   localStorage.removeItem(
      "token"
   );
}


export async function sendMessage(
   message:string,
   conversationId?:number
){

 const response=await fetch(
   `${API_BASE}/chat/`,
   {
      method:"POST",
      headers:authHeaders({
         "Content-Type":"application/json"
      }),
      body:JSON.stringify({
         message,
         provider:"ollama",
         model:"qwen2.5:7b",
         conversation_id:
            conversationId ?? null
      })
 });

 if(!response.ok)
    throw new Error("Chat request failed");

 return response.json();
}


export async function getConversation(id:number){

 const response=await fetch(
   `${API_BASE}/chat/${id}`,
   {
      headers:authHeaders()
   }
 );

 return response.json();
}


export async function getConversations(){

 const response=await fetch(
   `${API_BASE}/chat/conversations`,
   {
      headers:authHeaders()
   }
 );

 if(!response.ok)
    return [];

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
      headers:authHeaders(),
      body:formData
   }
 );

 if(!response.ok)
    throw new Error("Upload failed");

 return response.json();
}


export async function listUploads(){

 const response=await fetch(
   `${API_BASE}/upload/`,
   {
      headers:authHeaders()
   }
 );

 return response.json();
}


export async function deleteUpload(filename:string){

 const response=await fetch(
   `${API_BASE}/upload/${encodeURIComponent(filename)}`,
   {
      method:"DELETE",
      headers:authHeaders()
   }
 );

 return response.json();
}


export async function reindexUploads(){

 const response=await fetch(
   `${API_BASE}/upload/reindex`,
   {
      method:"POST",
      headers:authHeaders()
   }
 );

 return response.json();
}
