import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { MessageSquare, Users, Heart, Star, TrendingUp, Clock, Database, Languages, PenLine, Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/hooks/use-toast";
import {
  api,
  ApiError,
  type CommunityStats,
  type ForumCategory,
  type ForumCategoryCount,
  type ForumPost,
} from "@/lib/api";

const CATEGORY_META: Record<
  ForumCategory,
  { label: string; description: string; icon: JSX.Element }
> = {
  general: {
    label: "General Discussion",
    description: "General questions and discussions about NMT",
    icon: <MessageSquare className="h-5 w-5" />,
  },
  technical: {
    label: "Technical Support",
    description: "Get help with API integration and technical issues",
    icon: <Users className="h-5 w-5" />,
  },
  feature_requests: {
    label: "Feature Requests",
    description: "Suggest new features and improvements",
    icon: <Star className="h-5 w-5" />,
  },
  model_training: {
    label: "Model Training",
    description: "Discuss custom model training and optimization",
    icon: <TrendingUp className="h-5 w-5" />,
  },
  dataset_sharing: {
    label: "Dataset Sharing",
    description: "Share and discuss translation datasets",
    icon: <Heart className="h-5 w-5" />,
  },
};

const initials = (handle: string) =>
  handle
    .split(/[\s_]+/)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

const Community = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [stats, setStats] = useState<CommunityStats | null>(null);
  const [categories, setCategories] = useState<ForumCategoryCount[]>([]);
  const [posts, setPosts] = useState<ForumPost[]>([]);
  const [loadingPosts, setLoadingPosts] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newCategory, setNewCategory] = useState<ForumCategory>("general");
  const [newTitle, setNewTitle] = useState("");
  const [newBody, setNewBody] = useState("");
  const [posting, setPosting] = useState(false);

  const loadForum = () => {
    setLoadingPosts(true);
    Promise.all([api.getForumCategories(), api.listForumPosts()])
      .then(([cats, list]) => {
        setCategories(cats);
        setPosts(list);
      })
      .catch(() => {
        setCategories([]);
        setPosts([]);
      })
      .finally(() => setLoadingPosts(false));
  };

  useEffect(() => {
    api.getCommunityStats().then(setStats).catch(() => setStats(null));
    loadForum();
  }, []);

  const handleCreatePost = async () => {
    if (!newTitle.trim() || !newBody.trim()) return;
    setPosting(true);
    try {
      const created = await api.createForumPost({
        category: newCategory,
        title: newTitle.trim(),
        body: newBody.trim(),
      });
      setDialogOpen(false);
      setNewTitle("");
      setNewBody("");
      loadForum();
      navigate(`/community/posts/${created.id}`);
    } catch (error) {
      toast({
        title: "Couldn't create topic",
        description: error instanceof ApiError ? error.message : String(error),
        variant: "destructive",
      });
    } finally {
      setPosting(false);
    }
  };

  const countFor = (category: ForumCategory) =>
    categories.find((c) => c.category === category)?.post_count ?? 0;

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold tracking-tight mb-4">Community Forum</h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Join our vibrant community of developers, researchers, and translators. Share knowledge, get help, and collaborate on neural machine translation projects.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3 space-y-8">
          <div>
            <h2 className="text-2xl font-bold mb-6">Forum Categories</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {(Object.keys(CATEGORY_META) as ForumCategory[]).map((category) => {
                const meta = CATEGORY_META[category];
                return (
                  <Card key={category} className="hover:shadow-lg transition-shadow">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="text-primary">{meta.icon}</div>
                          <CardTitle className="text-lg">{meta.label}</CardTitle>
                        </div>
                        <Badge variant="secondary">{countFor(category)} posts</Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <CardDescription>{meta.description}</CardDescription>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">Recent Discussions</h2>
              <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <DialogTrigger asChild>
                  <Button
                    onClick={() => {
                      if (!isAuthenticated) {
                        toast({ title: "Please log in to start a topic" });
                        navigate("/login");
                      }
                    }}
                  >
                    New Topic
                  </Button>
                </DialogTrigger>
                {isAuthenticated && (
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Start a new discussion</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Category</label>
                        <Select
                          value={newCategory}
                          onValueChange={(v) => setNewCategory(v as ForumCategory)}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {(Object.keys(CATEGORY_META) as ForumCategory[]).map((category) => (
                              <SelectItem key={category} value={category}>
                                {CATEGORY_META[category].label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Title</label>
                        <Input
                          value={newTitle}
                          onChange={(e) => setNewTitle(e.target.value)}
                          maxLength={255}
                          placeholder="What's your question or topic?"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Body</label>
                        <Textarea
                          value={newBody}
                          onChange={(e) => setNewBody(e.target.value)}
                          rows={5}
                          maxLength={10000}
                          placeholder="Share the details..."
                        />
                      </div>
                      <Button
                        className="w-full"
                        onClick={handleCreatePost}
                        disabled={posting || !newTitle.trim() || !newBody.trim()}
                      >
                        {posting ? "Posting..." : "Post Topic"}
                      </Button>
                    </div>
                  </DialogContent>
                )}
              </Dialog>
            </div>

            {loadingPosts ? (
              <div className="flex items-center justify-center py-12 text-muted-foreground">
                <Loader2 className="h-5 w-5 animate-spin mr-2" />
                Loading discussions...
              </div>
            ) : posts.length === 0 ? (
              <p className="text-sm text-muted-foreground py-6">
                No discussions yet — start the first one.
              </p>
            ) : (
              <div className="space-y-4">
                {posts.map((post) => (
                  <Card
                    key={post.id}
                    className="hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => navigate(`/community/posts/${post.id}`)}
                  >
                    <CardContent className="pt-6">
                      <div className="flex items-start gap-4">
                        <Avatar>
                          <AvatarFallback>{initials(post.author_handle)}</AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <h3 className="font-semibold hover:text-primary transition-colors mb-2">
                            {post.title}
                          </h3>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground mb-2">
                            <span>by {post.author_handle}</span>
                            <Badge variant="outline" className="text-xs">
                              {CATEGORY_META[post.category]?.label ?? post.category}
                            </Badge>
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {new Date(post.created_at).toLocaleDateString()}
                            </div>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <MessageSquare className="h-4 w-4" />
                              {post.reply_count} {post.reply_count === 1 ? "reply" : "replies"}
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Community Impact</CardTitle>
              <CardDescription>Real activity on this platform — not a projection.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-2"><Database className="h-4 w-4" /> Datasets contributed</span>
                <span className="font-semibold">{stats?.total_datasets ?? "—"}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-2"><Languages className="h-4 w-4" /> Translations served</span>
                <span className="font-semibold">{stats?.total_translations ?? "—"}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-2"><PenLine className="h-4 w-4" /> Corrections submitted</span>
                <span className="font-semibold">{stats?.total_corrections ?? "—"}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-2"><Users className="h-4 w-4" /> Active contributors</span>
                <span className="font-semibold">{stats?.total_contributors ?? "—"}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Top Contributors</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <div>
                <p className="text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wide">Dataset uploads</p>
                {stats && stats.top_dataset_contributors.length > 0 ? (
                  <div className="space-y-2">
                    {stats.top_dataset_contributors.map((c, index) => (
                      <div key={c.handle} className="flex items-center gap-3">
                        <div className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-semibold">
                          {index + 1}
                        </div>
                        <div className="flex-1 font-medium text-sm">{c.handle}</div>
                        <Badge variant="outline" className="text-xs">{c.count}</Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No datasets uploaded yet.</p>
                )}
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wide">Review corrections</p>
                {stats && stats.top_reviewers.length > 0 ? (
                  <div className="space-y-2">
                    {stats.top_reviewers.map((c, index) => (
                      <div key={c.handle} className="flex items-center gap-3">
                        <div className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-semibold">
                          {index + 1}
                        </div>
                        <div className="flex-1 font-medium text-sm">{c.handle}</div>
                        <Badge variant="outline" className="text-xs">{c.count}</Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No corrections submitted yet.</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Community;
