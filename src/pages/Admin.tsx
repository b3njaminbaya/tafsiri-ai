import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { ArrowLeft, Loader2, Trash2, Users, BookOpen, Languages } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import {
  api,
  ApiError,
  type AdminUser,
  type BlogPost,
  type BlogPostDetail,
  type BlogPostStatus,
  type GlossaryTerm,
} from "@/lib/api";

const ROLES = ["user", "translator", "admin"] as const;

const UsersTab = () => {
  const { toast } = useToast();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [savingId, setSavingId] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    api
      .adminListUsers()
      .then(setUsers)
      .catch(() => setUsers([]))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const changeRole = async (user: AdminUser, role_name: string) => {
    setSavingId(user.id);
    try {
      const updated = await api.adminUpdateUser(user.id, { role_name });
      setUsers((prev) => prev.map((u) => (u.id === user.id ? updated : u)));
    } catch (error) {
      toast({
        title: "Couldn't change role",
        description: error instanceof ApiError ? error.message : String(error),
        variant: "destructive",
      });
    } finally {
      setSavingId(null);
    }
  };

  const toggleActive = async (user: AdminUser, is_active: boolean) => {
    setSavingId(user.id);
    try {
      const updated = await api.adminUpdateUser(user.id, { is_active });
      setUsers((prev) => prev.map((u) => (u.id === user.id ? updated : u)));
    } catch (error) {
      toast({
        title: "Couldn't update account",
        description: error instanceof ApiError ? error.message : String(error),
        variant: "destructive",
      });
    } finally {
      setSavingId(null);
    }
  };

  const filtered = users.filter((u) =>
    u.email.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin mr-2" />
        Loading users...
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Users ({users.length})</CardTitle>
        <CardDescription>Change roles or deactivate accounts.</CardDescription>
        <Input
          placeholder="Search by email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-sm mt-2"
        />
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Email</TableHead>
              <TableHead>Display name</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Active</TableHead>
              <TableHead>Verified</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((u) => (
              <TableRow key={u.id}>
                <TableCell className="font-medium">{u.email}</TableCell>
                <TableCell>{u.display_name ?? "—"}</TableCell>
                <TableCell>
                  <Select
                    value={u.role?.name ?? "user"}
                    onValueChange={(v) => changeRole(u, v)}
                    disabled={savingId === u.id}
                  >
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {ROLES.map((r) => (
                        <SelectItem key={r} value={r}>
                          {r}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </TableCell>
                <TableCell>
                  <Switch
                    checked={u.is_active}
                    disabled={savingId === u.id}
                    onCheckedChange={(checked) => toggleActive(u, checked)}
                  />
                </TableCell>
                <TableCell>
                  <Badge variant={u.is_verified ? "secondary" : "outline"}>
                    {u.is_verified ? "Verified" : "Unverified"}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
};

const GlossaryTab = () => {
  const { toast } = useToast();
  const [terms, setTerms] = useState<GlossaryTerm[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    domain: "",
    source_lang: "",
    target_lang: "",
    source_term: "",
    target_term: "",
  });
  const [creating, setCreating] = useState(false);

  const load = () => {
    setLoading(true);
    api
      .listGlossaryTerms()
      .then(setTerms)
      .catch(() => setTerms([]))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const canCreate =
    form.domain && form.source_lang && form.target_lang && form.source_term && form.target_term;

  const handleCreate = async () => {
    setCreating(true);
    try {
      await api.createGlossaryTerm(form);
      setForm({ domain: "", source_lang: "", target_lang: "", source_term: "", target_term: "" });
      load();
    } catch (error) {
      toast({
        title: "Couldn't add term",
        description: error instanceof ApiError ? error.message : String(error),
        variant: "destructive",
      });
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.deleteGlossaryTerm(id);
      setTerms((prev) => prev.filter((t) => t.id !== id));
    } catch (error) {
      toast({
        title: "Couldn't delete term",
        description: error instanceof ApiError ? error.message : String(error),
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Add a glossary term</CardTitle>
          <CardDescription>
            Forced into translation output whenever the source text matches, for the given domain
            and language pair.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <Input
            placeholder="Domain (e.g. medical)"
            value={form.domain}
            onChange={(e) => setForm((p) => ({ ...p, domain: e.target.value }))}
          />
          <Input
            placeholder="Source lang (en)"
            value={form.source_lang}
            onChange={(e) => setForm((p) => ({ ...p, source_lang: e.target.value }))}
          />
          <Input
            placeholder="Target lang (es)"
            value={form.target_lang}
            onChange={(e) => setForm((p) => ({ ...p, target_lang: e.target.value }))}
          />
          <Input
            placeholder="Source term"
            value={form.source_term}
            onChange={(e) => setForm((p) => ({ ...p, source_term: e.target.value }))}
          />
          <div className="flex gap-2">
            <Input
              placeholder="Target term"
              value={form.target_term}
              onChange={(e) => setForm((p) => ({ ...p, target_term: e.target.value }))}
            />
          </div>
          <Button
            onClick={handleCreate}
            disabled={!canCreate || creating}
            className="col-span-2 md:col-span-5 w-fit"
          >
            {creating ? "Adding..." : "Add term"}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Glossary terms ({terms.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-8 text-muted-foreground">
              <Loader2 className="h-5 w-5 animate-spin mr-2" />
              Loading...
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Domain</TableHead>
                  <TableHead>Pair</TableHead>
                  <TableHead>Source term</TableHead>
                  <TableHead>Target term</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {terms.map((t) => (
                  <TableRow key={t.id}>
                    <TableCell>{t.domain}</TableCell>
                    <TableCell>
                      {t.source_lang} → {t.target_lang}
                    </TableCell>
                    <TableCell>{t.source_term}</TableCell>
                    <TableCell>{t.target_term}</TableCell>
                    <TableCell>
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(t.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

const emptyPostForm = { title: "", category: "", excerpt: "", body: "", status: "draft" as BlogPostStatus };

const BlogTab = () => {
  const { toast } = useToast();
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState(emptyPostForm);
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true);
    api
      .adminListBlogPosts()
      .then(setPosts)
      .catch(() => setPosts([]))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const openNew = () => {
    setEditingId(null);
    setForm(emptyPostForm);
    setDialogOpen(true);
  };

  const openEdit = async (post: BlogPost) => {
    try {
      const detail: BlogPostDetail = await api.adminGetBlogPost(post.id);
      setEditingId(post.id);
      setForm({
        title: detail.title,
        category: detail.category ?? "",
        excerpt: detail.excerpt ?? "",
        body: detail.body,
        status: detail.status,
      });
      setDialogOpen(true);
    } catch (error) {
      toast({
        title: "Couldn't load post",
        description: error instanceof ApiError ? error.message : String(error),
        variant: "destructive",
      });
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = {
        title: form.title,
        category: form.category || null,
        excerpt: form.excerpt || null,
        body: form.body,
        status: form.status,
      };
      if (editingId) {
        await api.adminUpdateBlogPost(editingId, payload);
      } else {
        await api.adminCreateBlogPost(payload);
      }
      setDialogOpen(false);
      load();
    } catch (error) {
      toast({
        title: "Couldn't save post",
        description: error instanceof ApiError ? error.message : String(error),
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.adminDeleteBlogPost(id);
      setPosts((prev) => prev.filter((p) => p.id !== id));
    } catch (error) {
      toast({
        title: "Couldn't delete post",
        description: error instanceof ApiError ? error.message : String(error),
        variant: "destructive",
      });
    }
  };

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <div>
          <CardTitle>Blog posts ({posts.length})</CardTitle>
          <CardDescription>Create, edit, and publish articles.</CardDescription>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={openNew}>New post</Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>{editingId ? "Edit post" : "New post"}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Title</Label>
                <Input
                  value={form.title}
                  onChange={(e) => setForm((p) => ({ ...p, title: e.target.value }))}
                  maxLength={255}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Category</Label>
                  <Input
                    value={form.category}
                    onChange={(e) => setForm((p) => ({ ...p, category: e.target.value }))}
                    placeholder="e.g. Research"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Status</Label>
                  <Select
                    value={form.status}
                    onValueChange={(v) => setForm((p) => ({ ...p, status: v as BlogPostStatus }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="published">Published</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label>Excerpt</Label>
                <Textarea
                  value={form.excerpt}
                  onChange={(e) => setForm((p) => ({ ...p, excerpt: e.target.value }))}
                  rows={2}
                  maxLength={500}
                />
              </div>
              <div className="space-y-2">
                <Label>Body</Label>
                <Textarea
                  value={form.body}
                  onChange={(e) => setForm((p) => ({ ...p, body: e.target.value }))}
                  rows={10}
                />
              </div>
              <Button
                className="w-full"
                onClick={handleSave}
                disabled={saving || !form.title.trim() || !form.body.trim()}
              >
                {saving ? "Saving..." : editingId ? "Save changes" : "Create post"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center py-8 text-muted-foreground">
            <Loader2 className="h-5 w-5 animate-spin mr-2" />
            Loading...
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Status</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {posts.map((p) => (
                <TableRow key={p.id} className="cursor-pointer" onClick={() => openEdit(p)}>
                  <TableCell className="font-medium">{p.title}</TableCell>
                  <TableCell>{p.category ?? "—"}</TableCell>
                  <TableCell>
                    <Badge variant={p.status === "published" ? "default" : "outline"}>
                      {p.status}
                    </Badge>
                  </TableCell>
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(p.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
};

type AdminSection = "users" | "glossary" | "blog";

const ADMIN_NAV: { key: AdminSection; label: string; icon: typeof Users }[] = [
  { key: "users", label: "Users", icon: Users },
  { key: "glossary", label: "Glossary", icon: Languages },
  { key: "blog", label: "Blog", icon: BookOpen },
];

const ADMIN_SECTION_COPY: Record<AdminSection, { title: string; description: string }> = {
  users: { title: "Users", description: "Change roles or deactivate accounts." },
  glossary: {
    title: "Glossary",
    description: "Terms forced into translation output for a given domain and language pair.",
  },
  blog: { title: "Blog", description: "Create, edit, and publish articles." },
};

const Admin = () => {
  const [section, setSection] = useState<AdminSection>("users");

  return (
    // Not using SidebarInset here: it renders its own <main>, and this page
    // already sits inside App.tsx's <main className="flex-1">. Two nested
    // <main> landmarks is invalid HTML/bad a11y, so this hand-rolls the
    // equivalent layout on a plain div instead.
    //
    // App.tsx hides the site NavBar/Footer on /admin entirely — the
    // sidebar below is `fixed inset-y-0` (full viewport height,
    // scroll-independent), which fought with the sticky NavBar for the
    // same top strip and visually covered the Footer whenever it scrolled
    // into view underneath. Since there's no NavBar height to subtract
    // now, this is a plain min-h-screen instead of 100vh-4rem.
    <SidebarProvider className="min-h-screen">
      <Sidebar collapsible="icon">
        <SidebarHeader>
          <Link
            to="/"
            className="flex items-center gap-2 px-2 py-1 text-sm text-muted-foreground hover:text-brand transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Tafsiri AI
          </Link>
          <h2 className="font-semibold px-2 py-1">Admin Panel</h2>
        </SidebarHeader>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Manage</SidebarGroupLabel>
            <SidebarMenu>
              {ADMIN_NAV.map(({ key, label, icon: Icon }) => (
                <SidebarMenuItem key={key}>
                  <SidebarMenuButton
                    isActive={section === key}
                    onClick={() => setSection(key)}
                    className="data-[active=true]:text-brand data-[active=true]:font-medium"
                  >
                    <Icon className="h-4 w-4" />
                    <span>{label}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroup>
          {/* Room for a future "Overview" group with summary stat cards. */}
        </SidebarContent>
      </Sidebar>
      <div className="flex min-h-screen flex-1 flex-col bg-background">
        <div className="p-6 md:p-10 space-y-6">
          <div className="flex items-center gap-3">
            <SidebarTrigger className="md:hidden" />
            <div>
              <h1 className="text-3xl font-bold">{ADMIN_SECTION_COPY[section].title}</h1>
              <p className="text-muted-foreground">{ADMIN_SECTION_COPY[section].description}</p>
            </div>
          </div>
          {section === "users" && <UsersTab />}
          {section === "glossary" && <GlossaryTab />}
          {section === "blog" && <BlogTab />}
        </div>
      </div>
    </SidebarProvider>
  );
};

export default Admin;
