import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { MessageSquare, Users, Heart, Star, TrendingUp, Clock, Pin, Database, Languages, PenLine } from "lucide-react";
import { api, type CommunityStats } from "@/lib/api";

const Community = () => {
  const [stats, setStats] = useState<CommunityStats | null>(null);

  useEffect(() => {
    api.getCommunityStats().then(setStats).catch(() => setStats(null));
  }, []);
  const forumCategories = [
    {
      name: "General Discussion",
      description: "General questions and discussions about NMT",
      posts: 1247,
      icon: <MessageSquare className="h-5 w-5" />,
      color: "blue"
    },
    {
      name: "Technical Support",
      description: "Get help with API integration and technical issues",
      posts: 892,
      icon: <Users className="h-5 w-5" />,
      color: "green"
    },
    {
      name: "Feature Requests",
      description: "Suggest new features and improvements",
      posts: 345,
      icon: <Star className="h-5 w-5" />,
      color: "purple"
    },
    {
      name: "Model Training",
      description: "Discuss custom model training and optimization",
      posts: 567,
      icon: <TrendingUp className="h-5 w-5" />,
      color: "orange"
    },
    {
      name: "Dataset Sharing",
      description: "Share and discuss translation datasets",
      posts: 234,
      icon: <Heart className="h-5 w-5" />,
      color: "red"
    }
  ];

  const recentPosts = [
    {
      title: "Best practices for training domain-specific models",
      author: "Sarah Chen",
      avatar: "/placeholder.svg",
      category: "Model Training",
      replies: 23,
      likes: 45,
      time: "2 hours ago",
      pinned: true
    },
    {
      title: "API rate limits and optimization strategies",
      author: "Michael Rodriguez",
      avatar: "/placeholder.svg",
      category: "Technical Support",
      replies: 15,
      likes: 32,
      time: "4 hours ago",
      pinned: false
    },
    {
      title: "Sharing medical terminology dataset - 50K pairs",
      author: "Dr. Emma Wilson",
      avatar: "/placeholder.svg",
      category: "Dataset Sharing",
      replies: 8,
      likes: 67,
      time: "6 hours ago",
      pinned: false
    },
    {
      title: "Request: Support for code translation",
      author: "Alex Johnson",
      avatar: "/placeholder.svg",
      category: "Feature Requests",
      replies: 34,
      likes: 89,
      time: "1 day ago",
      pinned: false
    }
  ];

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
              {forumCategories.map((category, index) => (
                <Card key={index} className="hover:shadow-lg transition-shadow cursor-pointer">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="text-primary">{category.icon}</div>
                        <CardTitle className="text-lg">{category.name}</CardTitle>
                      </div>
                      <Badge variant="secondary">{category.posts} posts</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <CardDescription>{category.description}</CardDescription>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">Recent Discussions</h2>
              <Button>New Topic</Button>
            </div>
            <div className="space-y-4">
              {recentPosts.map((post, index) => (
                <Card key={index} className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="pt-6">
                    <div className="flex items-start gap-4">
                      <Avatar>
                        <AvatarImage src={post.avatar} />
                        <AvatarFallback>{post.author.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          {post.pinned && <Pin className="h-4 w-4 text-primary" />}
                          <h3 className="font-semibold hover:text-primary transition-colors">
                            {post.title}
                          </h3>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground mb-2">
                          <span>by {post.author}</span>
                          <Badge variant="outline" className="text-xs">{post.category}</Badge>
                          <div className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {post.time}
                          </div>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <MessageSquare className="h-4 w-4" />
                            {post.replies} replies
                          </div>
                          <div className="flex items-center gap-1">
                            <Heart className="h-4 w-4" />
                            {post.likes} likes
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
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

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" className="w-full justify-start">
                <MessageSquare className="h-4 w-4 mr-2" />
                Ask a Question
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Star className="h-4 w-4 mr-2" />
                Request Feature
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Heart className="h-4 w-4 mr-2" />
                Share Dataset
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Users className="h-4 w-4 mr-2" />
                Find Collaborators
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Community;