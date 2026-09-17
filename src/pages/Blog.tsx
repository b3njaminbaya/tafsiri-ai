import { useEffect, useMemo, useState } from "react";
import PageContainer from "@/components/layout/PageContainer";
import { Link, useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar, Loader2 } from "lucide-react";
import { api, type BlogPost } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

const Blog = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listBlogPosts()
      .then(setPosts)
      .catch(() => setPosts([]))
      .finally(() => setLoading(false));
  }, []);

  const categories = useMemo(() => {
    const counts = new Map<string, number>();
    for (const post of posts) {
      const key = post.category ?? "Uncategorized";
      counts.set(key, (counts.get(key) ?? 0) + 1);
    }
    return Array.from(counts.entries());
  }, [posts]);

  const [featured, ...rest] = posts;

  return (
    <PageContainer>
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold tracking-tight mb-4">Tafsiri AI Blog</h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Updates, research notes, and tutorials from the team.
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-24 text-muted-foreground">
          <Loader2 className="h-6 w-6 animate-spin mr-2" />
          Loading articles...
        </div>
      ) : posts.length === 0 ? (
        <p className="text-center text-muted-foreground py-16">
          No articles published yet — check back soon.
        </p>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-3">
            {featured && (
              <Card
                className="overflow-hidden mb-8 cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => navigate(`/blog/${featured.slug}`)}
              >
                <div className="p-8">
                  <div className="flex items-center gap-2 mb-4">
                    <Badge className="bg-primary/10 text-primary border-primary/20">Latest</Badge>
                    {featured.category && <Badge variant="outline">{featured.category}</Badge>}
                  </div>
                  <CardTitle className="text-2xl mb-3 hover:text-brand transition-colors">
                    {featured.title}
                  </CardTitle>
                  {featured.excerpt && (
                    <CardDescription className="text-base mb-4 leading-relaxed">
                      {featured.excerpt}
                    </CardDescription>
                  )}
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span>by {featured.author_handle}</span>
                    <div className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      {new Date(featured.published_at ?? featured.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              </Card>
            )}

            {rest.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {rest.map((post) => (
                  <Card
                    key={post.id}
                    className="hover:shadow-lg transition-shadow cursor-pointer"
                    onClick={() => navigate(`/blog/${post.slug}`)}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between mb-2">
                        {post.category && <Badge variant="outline">{post.category}</Badge>}
                      </div>
                      <CardTitle className="text-lg hover:text-brand transition-colors">
                        {post.title}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {post.excerpt && (
                        <CardDescription className="mb-4 leading-relaxed">
                          {post.excerpt}
                        </CardDescription>
                      )}
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span>{post.author_handle}</span>
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(post.published_at ?? post.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Categories</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {categories.map(([name, count]) => (
                    <div
                      key={name}
                      className="w-full flex items-center justify-between px-3 py-2 rounded-md text-sm"
                    >
                      <span>{name}</span>
                      <span className="text-muted-foreground">{count}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {user?.role?.name === "admin" && (
        <p className="text-center text-xs text-muted-foreground mt-16">
          <Link to="/admin" className="underline hover:text-brand">
            Manage posts in the admin panel
          </Link>
        </p>
      )}
    </PageContainer>
  );
};

export default Blog;
