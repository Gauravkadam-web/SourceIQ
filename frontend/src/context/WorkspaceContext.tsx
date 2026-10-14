"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { api, Workspace } from "../lib/api";

interface WorkspaceContextType {
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  isLoading: boolean;
  setActiveWorkspace: (ws: Workspace) => void;
  refreshWorkspaces: () => Promise<void>;
  createWorkspace: (name: string, description?: string) => Promise<Workspace>;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeWorkspace, setActiveWorkspace] = useState<Workspace | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshWorkspaces = async () => {
    try {
      const list = await api.listWorkspaces();
      setWorkspaces(list);

      if (list.length > 0) {
        // Keep active if exists, otherwise select first
        setActiveWorkspace((prev) => {
          if (prev && list.some((w) => w.id === prev.id)) {
            return prev;
          }
          return list[0];
        });
      } else {
        // Automatically create a default demo workspace
        const defaultWs = await api.createWorkspace("Default Workspace", "Default SourceIQ document intelligence workspace");
        setWorkspaces([defaultWs]);
        setActiveWorkspace(defaultWs);
      }
    } catch (err) {
      console.error("Failed to load workspaces:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const createWorkspace = async (name: string, description: string = "") => {
    const newWs = await api.createWorkspace(name, description);
    await refreshWorkspaces();
    setActiveWorkspace(newWs);
    return newWs;
  };

  useEffect(() => {
    refreshWorkspaces();
  }, []);

  return (
    <WorkspaceContext.Provider
      value={{
        workspaces,
        activeWorkspace,
        isLoading,
        setActiveWorkspace,
        refreshWorkspaces,
        createWorkspace,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error("useWorkspace must be used within a WorkspaceProvider");
  }
  return context;
}
