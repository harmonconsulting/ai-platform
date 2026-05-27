"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

import {
  login,
  logout,
  getConversation,
  getConversations,
  sendMessage,
  uploadFile,
  listUploads,
  deleteUpload,
  reindexUploads
} from "@/lib/api";

type Message = {
  role: string;
  content: string;
};

type Conversation = {
  id: number;
  title: string;
};

export default function Home() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [conversationId, setConversationId] = useState<number | undefined>();
  const [loading, setLoading] = useState(false);
  const [uploads, setUploads] = useState<any[]>([]);

const [email, setEmail] = useState("");
const [password, setPassword] = useState("");
const [authenticated, setAuthenticated] = useState(false);

  async function refreshConversations() {
    const data = await getConversations();
    setConversations(data);
  }

  async function refreshUploads() {
    const data = await listUploads();
    setUploads(data.files || []);
  }

  async function handleDeleteUpload(filename: string) {
    await deleteUpload(filename);
    await refreshUploads();
  }

  async function handleReindexUploads() {
    setLoading(true);

    try {
      const result = await reindexUploads();

      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: `Reindexed knowledge base. Files indexed: ${result.indexed_files?.length || 0}. Failed: ${result.failed_files?.length || 0}.`
        }
      ]);
    } catch (err) {
      console.error(err);

      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: "Reindex failed."
        }
      ]);
    } finally {
      setLoading(false);
      await refreshUploads();
    }
  }

  async function handleLogin() {
    try {
      setLoading(true);

      await login(
        email,
        password
      );

      setAuthenticated(true);

      await refreshConversations();
      await refreshUploads();

    } catch(err) {
      console.error(err);
      alert("Login failed");
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {

    logout();

    setAuthenticated(false);

    setMessages([]);
    setConversations([]);
    setUploads([]);
    setConversationId(undefined);
  }

  useEffect(() => {

    const token =
      localStorage.getItem(
        "token"
      );

    if(token){

      setAuthenticated(
        true
      );

      refreshConversations();
      refreshUploads();
    }

  }, []);





  async function loadConversation(id: number) {
    const data = await getConversation(id);
    setConversationId(id);
    setMessages(data.messages);
  }

  async function handleSend() {
    if (!input.trim()) return;

    const outgoing = input;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: outgoing }
    ]);

    setInput("");
    setLoading(true);

    try {
      const res = await sendMessage(outgoing, conversationId);

      setConversationId(res.conversation_id);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.response
        }
      ]);

      await refreshConversations();
    } catch (err) {
      console.error(err);

      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: "Message failed."
        }
      ]);
    } finally {
      setLoading(false);
    }
  }

  function newChat() {
    setConversationId(undefined);
    setMessages([]);
    setInput("");
  }

  async function handleUpload(file: File | null) {
    if (!file) return;

    setLoading(true);

    try {
      await uploadFile(file);
      await refreshUploads();
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: `Uploaded and indexed: ${file.name}`
        }
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: `Upload failed: ${file.name}`
        }
      ]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshConversations();
    refreshUploads();
  }, []);

  
if(!authenticated){

return (

<div className="min-h-screen flex items-center justify-center">

<div className="border rounded p-6 w-96 space-y-4">

<h1 className="text-xl font-bold">
Sellf AI Login
</h1>

<input
className="border p-2 w-full"
placeholder="Email"
value={email}
onChange={(e)=>setEmail(e.target.value)}
/>

<input
className="border p-2 w-full"
type="password"
placeholder="Password"
value={password}
onChange={(e)=>setPassword(e.target.value)}
/>

<button
className="border px-4 py-2 w-full"
disabled={loading}
onClick={handleLogin}
>
Login
</button>

</div>

</div>

);

}

return (

    <main className="flex min-h-screen bg-neutral-950 text-neutral-100">
      <button
        onClick={handleLogout}
        className="fixed right-4 top-4 z-50 rounded border border-neutral-700 bg-neutral-900 px-4 py-2 text-sm text-white hover:bg-neutral-800"
      >
        Logout
      </button>
      <aside className="w-72 border-r border-neutral-800 p-4">
        <button
          onClick={newChat}
          className="mb-4 w-full rounded border border-neutral-700 px-3 py-2 text-left"
        >
          + New chat
        </button>

        <div className="space-y-2">
          {conversations.map((c) => (
            <button
              key={c.id}
              onClick={() => loadConversation(c.id)}
              className="block w-full truncate rounded px-3 py-2 text-left hover:bg-neutral-800"
            >
              {c.title}
            </button>
          ))}
        </div>

        <div className="mt-8">
          <div className="mb-2 text-xs font-bold uppercase text-neutral-500">
            Uploaded Docs
          </div>

          <button
            onClick={handleReindexUploads}
            className="mb-3 w-full rounded border border-neutral-700 px-3 py-2 text-left text-xs hover:bg-neutral-800"
          >
            Reindex knowledge base
          </button>

          <div className="space-y-1">
            {uploads.map((file, i) => (
              <div
                key={i}
                className="flex items-center justify-between gap-2 rounded px-3 py-2 text-xs text-neutral-300"
                title={file.filename}
              >
                <span className="truncate">{file.filename}</span>

                <button
                  onClick={() => handleDeleteUpload(file.filename)}
                  className="text-neutral-500 hover:text-red-400"
                >
                  x
                </button>
              </div>
            ))}
          </div>
        </div>
      </aside>

      <section className="flex flex-1 flex-col">
        

        <div className="flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-3xl space-y-4">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`rounded p-4 ${
                  m.role === "user"
                    ? "bg-neutral-800"
                    : "bg-neutral-900 border border-neutral-800"
                }`}
              >
                <div className="mb-2 text-sm font-bold uppercase text-neutral-400">
                  {m.role}
                </div>
                <div className="prose prose-invert max-w-none"><ReactMarkdown>{m.content}</ReactMarkdown></div>
              </div>
            ))}

            {loading && (
              <div className="text-neutral-400">Thinking...</div>
            )}
          </div>
        </div>

        <div className="border-t border-neutral-800 p-4">
          <div className="mx-auto flex max-w-3xl gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSend();
              }}
              className="flex-1 rounded border border-neutral-700 bg-neutral-900 p-3 outline-none"
              placeholder="Message AI Platform..."
            />

            <label className="cursor-pointer rounded border border-neutral-700 px-4 py-3">
              Upload
              <input
                type="file"
                className="hidden"
                onChange={(e) => handleUpload(e.target.files?.[0] ?? null)}
              />
            </label>

            <button
              onClick={handleSend}
              disabled={loading}
              className="rounded bg-white px-5 py-3 font-medium text-black disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}
