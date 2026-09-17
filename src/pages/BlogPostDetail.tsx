import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Calendar, Loader2 } from "lucide-react";
import { api, type BlogPostDetail as BlogPostDetailType } from "@/lib/api";
import PageContainer from "@/components/layout/PageContainer";

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
      <PageContainer className="flex justify-center text-muted-foreground">
        <Loader2 className="h-6 w-6 animate-spin mr-2" />
        Loading article...
      </PageContainer>
    );
  }

  if (!post) {
    return (
      <PageContainer className="text-center space-y-4">
        <p className="text-muted-foreground">This article couldn't be found.</p>
        <Button variant="outline" onClick={() => navigate("/blog")}>
          Back to blog
        </Button>
      </PageContainer>
    );
  }

  return (
    <PageContainer className="max-w-3xl">
      <Link
        to="/blog"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-brand mb-6"
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
    </PageContainer>
  );
};

export default BlogPostDetail;
