import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ArrowLeft, Clock, Loader2, MessageSquare } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/hooks/use-toast";
import { api, ApiError, type ForumPostDetail } from "@/lib/api";
import PageContainer from "@/components/layout/PageContainer";

const CATEGORY_LABELS: Record<string, string> = {
  general: "General Discussion",
  technical: "Technical Support",
  feature_requests: "Feature Requests",
  model_training: "Model Training",
  dataset_sharing: "Dataset Sharing",
};

const initials = (handle: string) =>
  handle
    .split(/[\s_]+/)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

const ForumPost = () => {
  const { postId } = useParams<{ postId: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [post, setPost] = useState<ForumPostDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [replyBody, setReplyBody] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const load = () => {
    if (!postId) return;
    setLoading(true);
    api
      .getForumPost(Number(postId))
      .then(setPost)
      .catch(() => setPost(null))
      .finally(() => setLoading(false));
  };

  useEffect(load, [postId]);

  const submitReply = async () => {
    if (!postId || !replyBody.trim()) return;
    setSubmitting(true);
    try {
      await api.createForumReply(Number(postId), { body: replyBody.trim() });
      setReplyBody("");
      load();
    } catch (error) {
      toast({
        title: "Couldn't post your reply",
        description: error instanceof ApiError ? error.message : String(error),
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <PageContainer className="flex justify-center text-muted-foreground">
        <Loader2 className="h-6 w-6 animate-spin mr-2" />
        Loading discussion...
      </PageContainer>
    );
  }

  if (!post) {
    return (
      <PageContainer className="text-center space-y-4">
        <p className="text-muted-foreground">This discussion couldn't be found.</p>
        <Button variant="outline" onClick={() => navigate("/community")}>
          Back to forum
        </Button>
      </PageContainer>
    );
  }

  return (
    <PageContainer className="max-w-3xl">
      <Link
        to="/community"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-brand mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to forum
      </Link>

      <Card className="mb-8">
        <CardHeader>
          <Badge variant="outline" className="w-fit mb-2">
            {CATEGORY_LABELS[post.category] ?? post.category}
          </Badge>
          <CardTitle className="text-2xl">{post.title}</CardTitle>
          <div className="flex items-center gap-4 text-sm text-muted-foreground pt-2">
            <span>by {post.author_handle}</span>
            <div className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {new Date(post.created_at).toLocaleString()}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="whitespace-pre-wrap">{post.body}</p>
        </CardContent>
      </Card>

      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <MessageSquare className="h-5 w-5" />
        {post.replies.length} {post.replies.length === 1 ? "Reply" : "Replies"}
      </h2>

      <div className="space-y-4 mb-8">
        {post.replies.map((reply) => (
          <Card key={reply.id}>
            <CardContent className="pt-6">
              <div className="flex items-start gap-4">
                <Avatar>
                  <AvatarFallback>{initials(reply.author_handle)}</AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <div className="flex items-center gap-3 text-sm mb-1">
                    <span className="font-medium">{reply.author_handle}</span>
                    <span className="text-muted-foreground">
                      {new Date(reply.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="whitespace-pre-wrap">{reply.body}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        {post.replies.length === 0 && (
          <p className="text-sm text-muted-foreground">No replies yet — be the first.</p>
        )}
      </div>

      {isAuthenticated ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Post a reply</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Textarea
              value={replyBody}
              onChange={(e) => setReplyBody(e.target.value)}
              placeholder="Share your thoughts..."
              rows={4}
              maxLength={10000}
            />
            <Button onClick={submitReply} disabled={submitting || !replyBody.trim()}>
              {submitting ? "Posting..." : "Post reply"}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="pt-6 text-sm text-muted-foreground">
            <Link to="/login" className="text-brand hover:underline">
              Log in
            </Link>{" "}
            to join the discussion.
          </CardContent>
        </Card>
      )}
    </PageContainer>
  );
};

export default ForumPost;
