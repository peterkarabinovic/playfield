sealed trait Option[+A]
case class Some[+A](get: A) extends Option[A]
case object None extends Option[Nothing]

def mean(xs: Seq[Double]): Option[Double] =
    if (xs.isEmpty) None
    else Some(xs.sum / xs.length)

object Exceptions {

}

System.out.println(mean(List(1,2,3,4)));
System.out.println(classOf(List));
