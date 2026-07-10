import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Calendar, Loader2 } from "lucide-react";
import { api, type BlogPostDetail as BlogPostDetailType } from "@/lib/api";

const BlogPostDetail = () => {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [post, setPost] = useState<BlogPostDetailType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    api
      .getBlogPost(slug)
      .then(setPost)
      .catch(() => setPost(null))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-16 flex justify-center text-muted-foreground">
        <Loader2 className="h-6 w-6 animate-spin mr-2" />
        Loading article...
      </div>
    );
  }

  if (!post) {
    return (
      <div className="container mx-auto px-4 py-16 text-center space-y-4">
        <p className="text-muted-foreground">This article couldn't be found.</p>
        <Button variant="outline" onClick={() => navigate("/blog")}>
          Back to blog
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-16 max-w-3xl">
      <Link
        to="/blog"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-primary mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to blog
      </Link>

      {post.category && (
        <Badge variant="outline" className="mb-3">
          {post.category}
        </Badge>
      )}
      <h1 className="text-4xl font-bold tracking-tight mb-4">{post.title}</h1>
      <div className="flex items-center gap-4 text-sm text-muted-foreground mb-8">
        <span>by {post.author_handle}</span>
        <div className="flex items-center gap-1">
          <Calendar className="h-4 w-4" />
          {new Date(post.published_at ?? post.created_at).toLocaleDateString()}
        </div>
      </div>

      <div className="whitespace-pre-wrap leading-relaxed text-base">{post.body}</div>
    </div>
  );
};

export default BlogPostDetail;
